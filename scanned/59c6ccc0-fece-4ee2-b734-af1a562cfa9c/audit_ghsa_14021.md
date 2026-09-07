# [M] Pimcore Cross-site Scripting (XSS) in Predefined Properties delete

## Summary
Severity: Medium
Advisory: GHSA-q7cc-m6jw-m262
CVE: CVE-2023-2615
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2023-05-10
Source: https://github.com/advisories/GHSA-q7cc-m6jw-m262
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.5.21

## Details
### Impact
This vulnerability has the potential to steal a user's cookie and gain unauthorized access to that user's account through the stolen cookie or redirect users to other malicious sites.


### Patches
Update to version 10.5.21 or apply this patches manually
https://github.com/pimcore/pimcore/commit/7a799399e6843cd049e85da27ceb75b78505317f.patch

### Workarounds
Apply patches manually:
https://github.com/pimcore/pimcore/commit/7a799399e6843cd049e85da27ceb75b78505317f.patch

### References
https://huntr.dev/bounties/af9c360a-87f8-4e97-a24b-6db675ee942a/

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-q7cc-m6jw-m262
- https://nvd.nist.gov/vuln/detail/CVE-2023-2615
- https://github.com/pimcore/pimcore/commit/7a799399e6843cd049e85da27ceb75b78505317f
- https://github.com/pimcore/pimcore
- https://huntr.dev/bounties/af9c360a-87f8-4e97-a24b-6db675ee942a
