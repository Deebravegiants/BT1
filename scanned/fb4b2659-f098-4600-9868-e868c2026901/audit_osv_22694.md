# [M] CVE-2022-36354

## Summary
Severity: Medium
Advisory: CVE-2022-36354
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-36354
Type: osv

## Details
A heap out-of-bounds read vulnerability exists in the RLA format parser of OpenImageIO master-branch-9aeece7a and v2.3.19.0. More specifically, in the way run-length encoded byte spans are handled. A malformed RLA file can lead to an out-of-bounds read of heap metadata which can result in sensitive information leak. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2022-1629
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/36xxx/CVE-2022-36354.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-36354
