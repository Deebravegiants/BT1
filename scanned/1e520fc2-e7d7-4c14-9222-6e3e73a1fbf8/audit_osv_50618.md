# [H] CVE-2020-25682

## Summary
Severity: High
Advisory: CVE-2020-25682
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-01-20
Source: https://osv.dev/vulnerability/CVE-2020-25682
Type: osv

## Details
A flaw was found in dnsmasq before 2.83. A buffer overflow vulnerability was discovered in the way dnsmasq extract names from DNS packets before validating them with DNSSEC data. An attacker on the network, who can create valid DNS replies, could use this flaw to cause an overflow with arbitrary data in a heap-allocated memory, possibly executing code on the machine. The flaw is in the rfc1035.c:extract_name() function, which writes data to the memory pointed by name assuming MAXDNAME*2 bytes are available in the buffer. However, in some code execution paths, it is possible extract_name() gets passed an offset from the base buffer, thus reducing, in practice, the number of available bytes that can be written in the buffer. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability.

## References
- https://www.kb.cert.org/vuls/id/434904
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QGB7HL3OWHTLEPSMLDGOMXQKG3KM2QME/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WYW3IR6APUSKOYKL5FT3ACTIHWHGQY32/
- https://lists.debian.org/debian-lts-announce/2021/03/msg00027.html
- https://security.gentoo.org/glsa/202101-17
- https://www.debian.org/security/2021/dsa-4844
- https://www.jsof-tech.com/disclosures/dnspooq/
- https://bugzilla.redhat.com/show_bug.cgi?id=1882014
