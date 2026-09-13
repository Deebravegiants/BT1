# [M] CVE-2018-11713

## Summary
Severity: Medium
Advisory: CVE-2018-11713
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2018-06-04
Source: https://osv.dev/vulnerability/CVE-2018-11713
Type: osv

## Details
WebCore/platform/network/soup/SocketStreamHandleImplSoup.cpp in the libsoup network backend of WebKit, as used in WebKitGTK+ prior to version 2.20.0 or without libsoup 2.62.0, unexpectedly failed to use system proxy settings for WebSocket connections. As a result, users could be deanonymized by crafted web sites via a WebSocket connection.

## References
- https://security.gentoo.org/glsa/201808-04
- https://bugs.webkit.org/show_bug.cgi?id=126384
- https://trac.webkit.org/changeset/228088/webkit
