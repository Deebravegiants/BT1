# [H] SQL Injection found in Pimcore

## Summary
Severity: High
Advisory: GHSA-2v7p-f4qm-r5pc
CVE: CVE-2022-1429
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-04-23
Source: https://github.com/advisories/GHSA-2v7p-f4qm-r5pc
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.3.6

## Details
Pimcore is an open source data & experience management platform. A SQL injection was discovered in GridHelperService.php in GitHub repository pimcore/pimcore prior to 10.3.6.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-1429
- https://github.com/pimcore/pimcore/commit/523a735ab94f004459b84ffdfd3db784586bbd82
- https://github.com/pimcore/pimcore
- https://huntr.dev/bounties/cfba30b4-85fa-4499-9160-cd6e3119310e
