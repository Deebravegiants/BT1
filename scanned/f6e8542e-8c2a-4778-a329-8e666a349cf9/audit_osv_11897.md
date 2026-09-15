# [H] CVE-2018-1000027

## Summary
Severity: High
Advisory: CVE-2018-1000027
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-02-09
Source: https://osv.dev/vulnerability/CVE-2018-1000027
Type: osv

## Details
The Squid Software Foundation Squid HTTP Caching Proxy version prior to version 4.0.23 contains a NULL Pointer Dereference vulnerability in HTTP Response X-Forwarded-For header processing that can result in Denial of Service to all clients of the proxy. This attack appear to be exploitable via Remote HTTP server responding with an X-Forwarded-For header to certain types of HTTP request. This vulnerability appears to have been fixed in 4.0.23 and later.

## References
- https://usn.ubuntu.com/4059-2/
- https://github.com/squid-cache/squid/pull/129/files
- https://lists.debian.org/debian-lts-announce/2018/02/msg00001.html
- https://lists.debian.org/debian-lts-announce/2018/02/msg00002.html
- https://usn.ubuntu.com/3557-1/
- https://www.debian.org/security/2018/dsa-4122
- http://www.squid-cache.org/Advisories/SQUID-2018_2.txt
- http://www.squid-cache.org/Versions/v3/3.5/changesets/SQUID-2018_2.patch
- http://www.squid-cache.org/Versions/v4/changesets/SQUID-2018_2.patch
