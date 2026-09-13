# [H] CVE-2020-24606

## Summary
Severity: High
Advisory: CVE-2020-24606
Aliases: GHSA-vvj7-xjgq-g2jg
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-08-24
Source: https://osv.dev/vulnerability/CVE-2020-24606
Type: osv

## Details
Squid before 4.13 and 5.x before 5.0.4 allows a trusted peer to perform Denial of Service by consuming all available CPU cycles during handling of a crafted Cache Digest response message. This only occurs when cache_peer is used with the cache digests feature. The problem exists because peerDigestHandleReply() livelocking in peer_digest.cc mishandles EOF.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BE6FKUN7IGTIR2MEEMWYDT7N5EJJLZI2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BMTFLVB7GLRF2CKGFPZ4G4R5DIIPHWI3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HJJDI7JQFGQLVNCKMVY64LAFMKERAOK7/
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00012.html
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00017.html
- https://github.com/squid-cache/squid/security/advisories/GHSA-vvj7-xjgq-g2jg
- https://lists.debian.org/debian-lts-announce/2020/10/msg00005.html
- https://security.netapp.com/advisory/ntap-20210219-0007/
- https://security.netapp.com/advisory/ntap-20210226-0006/
- https://security.netapp.com/advisory/ntap-20210226-0007/
- https://usn.ubuntu.com/4477-1/
- https://usn.ubuntu.com/4551-1/
- https://www.debian.org/security/2020/dsa-4751
- http://www.squid-cache.org/Versions/v4/changesets/SQUID-2020_9.patch
