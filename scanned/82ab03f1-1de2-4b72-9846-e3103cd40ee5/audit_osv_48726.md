# [H] CVE-2018-12294

## Summary
Severity: High
Advisory: CVE-2018-12294
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-06-19
Source: https://osv.dev/vulnerability/CVE-2018-12294
Type: osv

## Details
WebCore/platform/graphics/texmap/TextureMapperLayer.cpp in WebKit, as used in WebKitGTK+ prior to version 2.20.2, is vulnerable to a use after free for a WebCore::TextureMapperLayer object.

## References
- http://www.securityfocus.com/archive/1/542087/100/0/threaded
- https://security.gentoo.org/glsa/201808-04
- https://trac.webkit.org/changeset/231300/webkit
- http://packetstormsecurity.com/files/148200/WebKitGTK-Data-Leak-Code-Execution.html
- https://bugs.webkit.org/show_bug.cgi?id=184729
- http://www.openwall.com/lists/oss-security/2018/06/14/1
