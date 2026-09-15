# [M] CVE-2023-52339

## Summary
Severity: Medium
Advisory: CVE-2023-52339
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2024-01-12
Source: https://osv.dev/vulnerability/CVE-2023-52339
Type: osv

## Details
In libebml before 1.4.5, an integer overflow in MemIOCallback.cpp can occur when reading or writing. It may result in buffer overflows.

## References
- https://github.com/Matroska-Org/libebml/blob/v1.x/NEWS.md
- https://github.com/Matroska-Org/libebml/compare/release-1.4.4...release-1.4.5
- https://lists.debian.org/debian-lts-announce/2025/01/msg00016.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/BJUXVOIRWPP7OFYUKQZDNJTSLWCPIZBH/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XNANFT4P6KL4WDQ3TV6QQ44NSC7WKLAB/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52339.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BJUXVOIRWPP7OFYUKQZDNJTSLWCPIZBH/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XNANFT4P6KL4WDQ3TV6QQ44NSC7WKLAB/
- https://nvd.nist.gov/vuln/detail/CVE-2023-52339
- https://github.com/Matroska-Org/libebml/issues/147
- https://github.com/Matroska-Org/libebml/pull/148
