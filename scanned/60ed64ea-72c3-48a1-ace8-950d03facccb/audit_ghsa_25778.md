# [M] Cross-site Scripting in Pimcore

## Summary
Severity: Medium
Advisory: GHSA-q67f-3jq4-mww2
CVE: CVE-2022-0831
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-03-05
Source: https://github.com/advisories/GHSA-q67f-3jq4-mww2
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.3.3

## Details
Pimcore version 10.3.2 and prior is vulnerable to stored cross-site scripting. A patch is available and anticipated to be part of version 10.3.3.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0831
- https://github.com/pimcore/pimcore/commit/e786fd44aac46febdbf916ed6c328fbe645d80bf
- https://github.com/pimcore/pimcore
- https://huntr.dev/bounties/4152e3a7-27a1-49eb-a6eb-a57506af104f
