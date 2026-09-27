# [C] CVE-2018-1000005

## Summary
Severity: Critical
Advisory: CVE-2018-1000005
Aliases: CURL-CVE-2018-1000005
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2018-01-24
Source: https://osv.dev/vulnerability/CVE-2018-1000005
Type: osv

## Details
libcurl 7.49.0 to and including 7.57.0 contains an out bounds read in code handling HTTP/2 trailers. It was reported (https://github.com/curl/curl/pull/2231) that reading an HTTP/2 trailer could mess up future trailers since the stored size was one byte less than required. The problem is that the code that creates HTTP/1-like headers from the HTTP/2 trailer data once appended a string like `:` to the target buffer, while this was recently changed to `: ` (a space was added after the colon) but the following math wasn't updated correspondingly. When accessed, the data is read out of bounds and causes either a crash or that the (too large) data gets passed to client write. This could lead to a denial-of-service situation or an information disclosure if someone has a service that echoes back or uses the trailers for something.

## References
- http://www.securitytracker.com/id/1040273
- https://access.redhat.com/errata/RHSA-2019:1543
- https://usn.ubuntu.com/3554-1/
- https://www.debian.org/security/2018/dsa-4098
- https://curl.haxx.se/docs/adv_2018-824a.html
- https://github.com/curl/curl/pull/2231
