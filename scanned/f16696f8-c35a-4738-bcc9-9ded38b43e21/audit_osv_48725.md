# [H] CVE-2018-12293

## Summary
Severity: High
Advisory: CVE-2018-12293
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-06-19
Source: https://osv.dev/vulnerability/CVE-2018-12293
Type: osv

## Details
The getImageData function in the ImageBufferCairo class in WebCore/platform/graphics/cairo/ImageBufferCairo.cpp in WebKit, as used in WebKitGTK+ prior to version 2.20.3 and WPE WebKit prior to version 2.20.1, is vulnerable to a heap-based buffer overflow triggered by an integer overflow, which could be abused by crafted HTML content.

## References
- https://www.exploit-db.com/exploits/45205/
- http://www.securityfocus.com/archive/1/542087/100/0/threaded
- http://packetstormsecurity.com/files/148200/WebKitGTK-Data-Leak-Code-Execution.html
- https://security.gentoo.org/glsa/201808-04
- https://usn.ubuntu.com/3687-1/
- https://bugs.webkit.org/show_bug.cgi?id=186384
- https://trac.webkit.org/changeset/232618
- http://www.openwall.com/lists/oss-security/2018/06/14/1
