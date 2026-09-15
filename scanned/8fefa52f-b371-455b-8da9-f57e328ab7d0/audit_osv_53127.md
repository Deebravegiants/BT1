# [H] CVE-2022-30293

## Summary
Severity: High
Advisory: CVE-2022-30293
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-05-06
Source: https://osv.dev/vulnerability/CVE-2022-30293
Type: osv

## Details
In WebKitGTK through 2.36.0 (and WPE WebKit), there is a heap-based buffer overflow in WebCore::TextureMapperLayer::setContentsLayer in WebCore/platform/graphics/texmap/TextureMapperLayer.cpp.

## References
- http://www.openwall.com/lists/oss-security/2022/05/30/1
- https://security.gentoo.org/glsa/202208-39
- https://www.debian.org/security/2022/dsa-5154
- https://www.debian.org/security/2022/dsa-5155
- https://bugs.webkit.org/show_bug.cgi?id=237187
- https://github.com/ChijinZ/security_advisories/tree/master/webkitgtk-2.36.0
