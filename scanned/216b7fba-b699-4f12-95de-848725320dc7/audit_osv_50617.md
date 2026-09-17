# [H] CVE-2020-25681

## Summary
Severity: High
Advisory: CVE-2020-25681
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-01-20
Source: https://osv.dev/vulnerability/CVE-2020-25681
Type: osv

## Details
A flaw was found in dnsmasq before version 2.83. A heap-based buffer overflow was discovered in the way RRSets are sorted before validating with DNSSEC data. An attacker on the network, who can forge DNS replies such as that they are accepted as valid, could use this flaw to cause a buffer overflow with arbitrary data in a heap memory segment, possibly executing code on the machine. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability.

## References
- https://www.kb.cert.org/vuls/id/434904
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QGB7HL3OWHTLEPSMLDGOMXQKG3KM2QME/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WYW3IR6APUSKOYKL5FT3ACTIHWHGQY32/
- https://www.debian.org/security/2021/dsa-4844
- https://www.jsof-tech.com/disclosures/dnspooq/
- https://lists.debian.org/debian-lts-announce/2021/03/msg00027.html
- https://security.gentoo.org/glsa/202101-17
- https://bugzilla.redhat.com/show_bug.cgi?id=1881875
