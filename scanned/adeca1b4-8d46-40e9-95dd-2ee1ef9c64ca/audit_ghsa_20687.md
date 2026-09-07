# [M] Moodle XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-cwhp-rqfr-8462
CVE: CVE-2020-1691
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-08-06
Source: https://github.com/advisories/GHSA-cwhp-rqfr-8462
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.8 <3.8.1

## Details
In Moodle 3.8, messages required extra sanitizing before updating the conversation overview, to prevent the risk of stored cross-site scripting.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1691
- https://github.com/moodle/moodle/commit/4e809346537e230cbff8235bfee0e7e151e4e9f9
- https://moodle.org/mod/forum/discuss.php?d=395953
