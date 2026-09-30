# [H] CVE-2023-2977

## Summary
Severity: High
Advisory: CVE-2023-2977
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2023-06-01
Source: https://osv.dev/vulnerability/CVE-2023-2977
Type: osv

## Details
A vulnerbility was found in OpenSC. This security flaw cause a buffer overrun vulnerability in pkcs15 cardos_have_verifyrc_package. The attacker can supply a smart card package with malformed ASN1 context. The cardos_have_verifyrc_package function scans the ASN1 buffer for 2 tags, where remaining length is wrongly caculated due to moved starting pointer. This leads to possible heap-based buffer oob read. In cases where ASAN is enabled while compiling this causes a crash. Further info leak or more damage is possible.

## References
- https://access.redhat.com/security/cve/CVE-2023-2977
- https://lists.debian.org/debian-lts-announce/2024/12/msg00026.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/2xxx/CVE-2023-2977.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FJD4Q4AJSGE5UIJI7OUYZY4HGGCVYQNI/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LAR54OV6EHA56B4XJF6RNPQ4HJ2ITU66/
- https://nvd.nist.gov/vuln/detail/CVE-2023-2977
- https://bugzilla.redhat.com/show_bug.cgi?id=2211088
- https://github.com/OpenSC/OpenSC/issues/2785
- https://github.com/OpenSC/OpenSC/pull/2787
- https://lists.debian.org/debian-lts-announce/2023/06/msg00025.html
