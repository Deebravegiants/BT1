# [H] CVE-2018-11712

## Summary
Severity: High
Advisory: CVE-2018-11712
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-06-04
Source: https://osv.dev/vulnerability/CVE-2018-11712
Type: osv

## Details
WebCore/platform/network/soup/SocketStreamHandleImplSoup.cpp in the libsoup network backend of WebKit, as used in WebKitGTK+ versions 2.20.0 and 2.20.1, failed to perform TLS certificate verification for WebSocket connections.

## References
- https://security.gentoo.org/glsa/201808-04
- https://trac.webkit.org/changeset/230886/webkit
- https://bugs.webkit.org/show_bug.cgi?id=184804
