# [M] Privileges Memory Corruption (Out-of-bound write)

## Summary
Severity: Medium
Advisory: CVE-2023-40307
Aliases: GHSA-rgq4-wxpj-5jv9
CVSS: 6.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:L)
Published: 2023-09-28
Source: https://osv.dev/vulnerability/CVE-2023-40307
Type: osv

## Details
An attacker with standard privileges on macOS when requesting administrator privileges from the application can submit input which causes a buffer overflow resulting in a crash of the application. This could make the application unavailable and allow reading or modification of data.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/40xxx/CVE-2023-40307.json
- https://github.com/SAP/macOS-enterprise-privileges/security/advisories/GHSA-rgq4-wxpj-5jv9
- https://nvd.nist.gov/vuln/detail/CVE-2023-40307
