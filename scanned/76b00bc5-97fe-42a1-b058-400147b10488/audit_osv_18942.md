# [M] CVE-2020-5238

## Summary
Severity: Medium
Advisory: CVE-2020-5238
Aliases: GHSA-7gc6-9qr5-hc85
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-07-01
Source: https://osv.dev/vulnerability/CVE-2020-5238
Type: osv

## Details
The table extension in GitHub Flavored Markdown before version 0.29.0.gfm.1 takes O(n * n) time to parse certain inputs. An attacker could craft a markdown table which would take an unreasonably long time to process, causing a denial of service. This issue does not affect the upstream cmark project. The issue has been fixed in version 0.29.0.gfm.1.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TCDHBTUFIOYRIS5HAS6PZNBNMB7IOAX3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WMQFOQQCWOAMQ4I2XIVCVOXXIJ75HDCW/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZGJH2A4VAV54X6NSCNNGSEIGIIY5N2VR/
- https://github.com/github/cmark-gfm/security/advisories/GHSA-7gc6-9qr5-hc85
- https://github.com/github/cmark-gfm/commit/85d895289c5ab67f988ca659493a64abb5fec7b4
