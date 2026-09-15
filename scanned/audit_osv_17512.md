# [M] CVE-2020-15811

## Summary
Severity: Medium
Advisory: CVE-2020-15811
Aliases: GHSA-c7p8-xqhm-49wv
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2020-09-02
Source: https://osv.dev/vulnerability/CVE-2020-15811
Type: osv

## Details
An issue was discovered in Squid before 4.13 and 5.x before 5.0.4. Due to incorrect data validation, HTTP Request Splitting attacks may succeed against HTTP and HTTPS traffic. This leads to cache poisoning. This allows any client, including browser scripts, to bypass local security and poison the browser cache and any downstream caches with content from an arbitrary source. Squid uses a string search instead of parsing the Transfer-Encoding header to find chunked encoding. This allows an attacker to hide a second request inside Transfer-Encoding: it is interpreted by Squid as chunked and split out into a second request delivered upstream. Squid will then deliver two distinct responses to the client, corrupting any downstream caches.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00012.html
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00017.html
- https://lists.debian.org/debian-lts-announce/2020/10/msg00005.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BE6FKUN7IGTIR2MEEMWYDT7N5EJJLZI2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BMTFLVB7GLRF2CKGFPZ4G4R5DIIPHWI3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HJJDI7JQFGQLVNCKMVY64LAFMKERAOK7/
- https://security.netapp.com/advisory/ntap-20210219-0007/
- https://security.netapp.com/advisory/ntap-20210226-0006/
- https://security.netapp.com/advisory/ntap-20210226-0007/
- https://usn.ubuntu.com/4477-1/
- https://usn.ubuntu.com/4551-1/
- https://www.debian.org/security/2020/dsa-4751
- https://github.com/squid-cache/squid/security/advisories/GHSA-c7p8-xqhm-49wv
