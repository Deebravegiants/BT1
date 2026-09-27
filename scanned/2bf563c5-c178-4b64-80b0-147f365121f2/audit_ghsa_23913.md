# [C] Centreon RCE Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-c8qc-cp8v-prpx
CVE: CVE-2018-11587
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-c8qc-cp8v-prpx
Type: github-advisory

## Affected
- Packagist: `centreon/centreon` — affected 3.4.6
- Packagist: `centreon/centreon` — affected >=2.8.23 <2.8.24

## Details
There is Remote Code Execution in Centreon 3.4.6 including Centreon Web 2.8.23 via the RPN value in the Virtual Metric form in centreonGraph.class.php.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-11587
- https://github.com/centreon/centreon-archived/pull/6263
- https://github.com/centreon/centreon-archived/pull/6263/commits/fb438e6aaf133cc5f9d25130653ba8fdc6ecf51f
- https://documentation.centreon.com/docs/centreon/en/latest/release_notes/centreon-2.8/centreon-2.8.24.html
