# [M] vantage6 vulnerable to Observable Response Discrepancy

## Summary
Severity: Medium
Advisory: GHSA-36gx-9q6h-g429
CVE: CVE-2022-39228
CWE: CWE-203, CWE-204
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L (CVSS_V3)
Published: 2023-02-28
Source: https://github.com/advisories/GHSA-36gx-9q6h-g429
Type: github-advisory

## Affected
- PyPI: `vantage6` — affected >=0 <3.8.0

## Details
### Impact
We are incorporating the password policies listed in https://github.com/vantage6/vantage6/issues/59. One measure is that we don't let the user know in case of wrong username/password combination if the username actually exists, to prevent that bots can guess usernames. However, if a wrong password is entered a number of times, the user account is blocked temporarily. This way you could still find out which usernames exist.

### Patches
Update to 3.8.0+

### Workarounds
No

### References
https://github.com/vantage6/vantage6/issues/59

### For more information
If you have any questions or comments about this advisory:
* Email us at [vantage6@iknl.nl](mailto:vantage6@iknl.nl)

## References
- https://github.com/vantage6/vantage6/security/advisories/GHSA-36gx-9q6h-g429
- https://nvd.nist.gov/vuln/detail/CVE-2022-39228
- https://github.com/vantage6/vantage6/issues/59
- https://github.com/vantage6/vantage6/pull/281
- https://github.com/vantage6/vantage6/commit/ab4381c35d24add06f75d5a8a284321f7a340bd2
- https://github.com/pypa/advisory-database/tree/main/vulns/vantage6/PYSEC-2023-313.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/vantage6/PYSEC-2023-52.yaml
- https://github.com/vantage6/vantage6
