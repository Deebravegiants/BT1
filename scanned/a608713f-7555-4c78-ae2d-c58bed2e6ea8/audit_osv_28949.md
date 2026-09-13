# [M] CVE-2024-38446

## Summary
Severity: Medium
Advisory: CVE-2024-38446
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2024-07-17
Source: https://osv.dev/vulnerability/CVE-2024-38446
Type: osv

## Details
NATO NCI ANET 3.4.1 mishandles report ownership. A user can create a report and, despite the restrictions imposed by the UI, change the author of that report to an arbitrary user (without their consent or knowledge) via a modified UUID in a POST request.

## References
- https://www.linkedin.com/pulse/idors-ncia-anet-v341-visionspace-technologies-hepxe
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38446.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38446
