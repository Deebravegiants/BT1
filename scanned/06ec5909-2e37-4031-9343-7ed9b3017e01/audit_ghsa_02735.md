# [H] Missing Authorization in TeamPass

## Summary
Severity: High
Advisory: GHSA-gmr7-m73x-6c9q
CVE: CVE-2020-11671
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-07-26
Source: https://github.com/advisories/GHSA-gmr7-m73x-6c9q
Type: github-advisory

## Affected
- Packagist: `nilsteampassnet/teampass` — affected >=0

## Details
Lack of authorization controls in REST API functions in TeamPass through 2.1.27.36 allows any TeamPass user with a valid API token to become a TeamPass administrator and read/modify all passwords via authenticated api/index.php REST API calls. NOTE: the API is not available by default.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-11671
- https://github.com/nilsteampassnet/TeamPass/issues/2765
