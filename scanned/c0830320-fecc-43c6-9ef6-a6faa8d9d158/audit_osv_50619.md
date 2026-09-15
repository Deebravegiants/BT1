# [M] CVE-2020-25683

## Summary
Severity: Medium
Advisory: CVE-2020-25683
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-01-20
Source: https://osv.dev/vulnerability/CVE-2020-25683
Type: osv

## Details
A flaw was found in dnsmasq before version 2.83. A heap-based buffer overflow was discovered in dnsmasq when DNSSEC is enabled and before it validates the received DNS entries. A remote attacker, who can create valid DNS replies, could use this flaw to cause an overflow in a heap-allocated memory. This flaw is caused by the lack of length checks in rfc1035.c:extract_name(), which could be abused to make the code execute memcpy() with a negative size in get_rdata() and cause a crash in dnsmasq, resulting in a denial of service. The highest threat from this vulnerability is to system availability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WYW3IR6APUSKOYKL5FT3ACTIHWHGQY32/
- https://www.kb.cert.org/vuls/id/434904
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QGB7HL3OWHTLEPSMLDGOMXQKG3KM2QME/
- https://security.gentoo.org/glsa/202101-17
- https://www.debian.org/security/2021/dsa-4844
- https://www.jsof-tech.com/disclosures/dnspooq/
- https://lists.debian.org/debian-lts-announce/2021/03/msg00027.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1882018
