# [M] CVE-2020-15810

## Summary
Severity: Medium
Advisory: CVE-2020-15810
Aliases: GHSA-3365-q9qx-f98m
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2020-09-02
Source: https://osv.dev/vulnerability/CVE-2020-15810
Type: osv

## Details
An issue was discovered in Squid before 4.13 and 5.x before 5.0.4. Due to incorrect data validation, HTTP Request Smuggling attacks may succeed against HTTP and HTTPS traffic. This leads to cache poisoning. This allows any client, including browser scripts, to bypass local security and poison the proxy cache and any downstream caches with content from an arbitrary source. When configured for relaxed header parsing (the default), Squid relays headers containing whitespace characters to upstream servers. When this occurs as a prefix to a Content-Length header, the frame length specified will be ignored by Squid (allowing for a conflicting length to be used from another Content-Length header) but relayed upstream.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BE6FKUN7IGTIR2MEEMWYDT7N5EJJLZI2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BMTFLVB7GLRF2CKGFPZ4G4R5DIIPHWI3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HJJDI7JQFGQLVNCKMVY64LAFMKERAOK7/
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00012.html
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00017.html
- https://github.com/squid-cache/squid/security/advisories/GHSA-3365-q9qx-f98m
- https://lists.debian.org/debian-lts-announce/2020/10/msg00005.html
- https://security.netapp.com/advisory/ntap-20210219-0007/
- https://security.netapp.com/advisory/ntap-20210226-0006/
- https://security.netapp.com/advisory/ntap-20210226-0007/
- https://usn.ubuntu.com/4477-1/
- https://usn.ubuntu.com/4551-1/
- https://www.debian.org/security/2020/dsa-4751
