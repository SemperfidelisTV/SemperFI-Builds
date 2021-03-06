"""
    Kodi urlresolver plugin
    Copyright (C) 2014  smokdpi

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from t0mm0.common.net import Net
from urlresolver import common
from urlresolver.plugnplay import Plugin
from urlresolver.plugnplay.interfaces import UrlResolver
from urlresolver.plugnplay.interfaces import PluginSettings
import re
import xbmc
from lib import jsunpack

class FlashxResolver(Plugin, UrlResolver, PluginSettings):
    implements = [UrlResolver, PluginSettings]
    name = "flashx"
    domains = ["flashx.tv"]

    def __init__(self):
        p = self.get_setting('priority') or 100
        self.priority = int(p)
        self.net = Net()
        self.pattern = '//((?:www.|play.)?flashx.tv)/(?:embed-|dl\?)?([0-9a-zA-Z/-]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'Referer': web_url}
        stream_url = self.__get_link(web_url, media_id, headers)
        if stream_url is None:
            headers['User-Agent'] = common.IOS_USER_AGENT
            stream_url = self.__get_link(web_url, media_id, headers)
        
        if stream_url is not None:
            return stream_url + '|User-Agent=%s' % (common.IE_USER_AGENT)

        raise UrlResolver.ResolverError('File not found')

    def __get_link(self, web_url, media_id, headers):
        html = self.net.http_GET(web_url, headers=headers).content
        data = {}
        r = re.findall(r'type="hidden"\s*name="([^"]+)"\s*value="([^"]+)', html)
        for name, value in r:
            data[name] = value
        data['imhuman'] = 'Proceed+to+video'
        url = 'http://www.flashx.tv/dl?%s' % (media_id)
        xbmc.sleep(6000)
        html = self.net.http_POST(url, form_data=data, headers=headers).content
        
        best = 0
        best_link = ''
        for packed in re.findall("<script[^>]*>(eval\(function.*?)</script>", html, re.DOTALL):
            unpacked = jsunpack.unpack(packed)
            for stream in re.findall('file\s*:\s*"(http.*?)"\s*,\s*label\s*:\s*"(\d+)', unpacked, re.DOTALL):
                if int(stream[1]) > best:
                    best = int(stream[1])
                    best_link = stream[0]

        if best_link:
            return best_link
        else:
            raise UrlResolver.ResolverError('Unable to resolve Flashx link. Filelink not found.')
        
    def get_url(self, host, media_id):
        return 'http://www.flashx.tv/%s.html' % media_id

    def get_host_and_id(self, url):
        r = re.search(self.pattern, url)
        if r: return r.groups()
        else: return False

    def valid_url(self, url, host):
        return re.search(self.pattern, url) or self.name in host

    def get_settings_xml(self):
        xml = PluginSettings.get_settings_xml(self)
        xml += '<setting id="%s_auto_pick" type="bool" label="Automatically pick best quality" default="false" visible="true"/>' % (self.__class__.__name__)
        return xml
