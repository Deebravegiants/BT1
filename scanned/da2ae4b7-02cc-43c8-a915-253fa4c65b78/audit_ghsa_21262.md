# [C] Badaso vulnerable to Remote Code Execution via malicious file upload

## Summary
Severity: Critical
Advisory: GHSA-fwvc-9xhj-26v5
CVE: CVE-2022-41711
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-10-26
Source: https://github.com/advisories/GHSA-fwvc-9xhj-26v5
Type: github-advisory

## Affected
- Packagist: `badaso/core` — affected >=0 <2.6.1

## Details
Badaso allows an unauthenticated remote attacker to execute arbitrary code remotely on the server. This is possible because the application does not properly validate the data uploaded by users.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-41711
- https://github.com/uasoft-indonesia/badaso/issues/802
- https://github.com/uasoft-indonesia/badaso/commit/22250eca7c364d991ce9e0a723941eae4889d6f9
- https://fluidattacks.com/advisories/harlow
- https://github.com/uasoft-indonesia/badaso
