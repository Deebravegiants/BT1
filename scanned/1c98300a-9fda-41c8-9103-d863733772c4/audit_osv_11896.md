# [H] CVE-2018-1000024

## Summary
Severity: High
Advisory: CVE-2018-1000024
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-02-09
Source: https://osv.dev/vulnerability/CVE-2018-1000024
Type: osv

## Details
The Squid Software Foundation Squid HTTP Caching Proxy version 3.0 to 3.5.27, 4.0 to 4.0.22 contains a Incorrect Pointer Handling vulnerability in ESI Response Processing that can result in Denial of Service for all clients using the proxy.. This attack appear to be exploitable via Remote server delivers an HTTP response payload containing valid but unusual ESI syntax.. This vulnerability appears to have been fixed in 4.0.23 and later.

## References
- https://usn.ubuntu.com/4059-2/
- http://www.squid-cache.org/Versions/
- https://lists.debian.org/debian-lts-announce/2018/02/msg00001.html
- https://usn.ubuntu.com/3557-1/
- https://www.debian.org/security/2018/dsa-4122
- http://www.squid-cache.org/Advisories/SQUID-2018_1.txt
