# [C] Dolibarr Improper Restriction of Excessive Authentication Attempts

## Summary
Severity: Critical
Advisory: GHSA-m5c3-3gvf-q8j5
CVE: CVE-2020-7995
CWE: CWE-287, CWE-307
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-m5c3-3gvf-q8j5
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected 10.0.6

## Details
The htdocs/index.php?mainmenu=home login page in Dolibarr 10.0.6 allows an unlimited rate of failed authentication attempts.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7995
- https://github.com/Dolibarr/dolibarr
- https://github.com/tufangungor/tufangungor.github.io/blob/master/_posts/2020-01-19-dolibarr-10.0.6-brute-force.md
- https://tufangungor.github.io/exploit/2020/01/18/dolibarr-10.0.6-brute-force.html
- http://packetstormsecurity.com/files/163541/Dolibarr-ERP-CRM-10.0.6-Login-Brute-Forcer.html
