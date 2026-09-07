# [H] Authenticated RCE in Zen Cart 1.5.5e

## Summary
Severity: High
Advisory: GHSA-c9r9-3h38-r7vj
CVE: CVE-2017-11675
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-c9r9-3h38-r7vj
Type: github-advisory

## Affected
- Packagist: `zencart/zencart` — affected >=0

## Details
The traverseStrictSanitize function in admin_dir/includes/classes/AdminRequestSanitizer.php in ZenCart 1.5.5e mishandles key strings, which allows remote authenticated users to execute arbitrary PHP code by placing that code into an invalid array index of the admin_name array parameter to admin_dir/login.php, if there is an export of an error-log entry for that invalid array index.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-11675
- https://github.com/imp0wd3r/vuln-papers/tree/master/zencart-155e-auth-rce
