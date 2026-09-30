# [C] NetAlertX has Password Bypass Vulnerability due to Loose Comparison in PHP

## Summary
Severity: Critical
Advisory: CVE-2025-48952
Aliases: GHSA-4p4p-vq2v-9489
CVSS: 9.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L)
Published: 2025-07-04
Source: https://osv.dev/vulnerability/CVE-2025-48952
Type: osv

## Details
NetAlertX is a network, presence scanner, and alert framework. Prior to version 25.6.7, a vulnerability in the authentication logic allows users to bypass password verification using SHA-256 magic hashes, due to loose comparison in PHP. In vulnerable versions of the application, a password comparison is performed using the `==` operator at line 40 in front/index.php. This introduces a security issue where specially crafted "magic hash" values that evaluate to true in a loose comparison can bypass authentication. Because of the use of `==` instead of the strict `===`, different strings that begin with 0e and are followed by only digits can be interpreted as scientific notation (i.e., zero) and treated as equal. This issue falls under the Login Bypass vulnerability class. Users with certain "weird" passwords that produce magic hashes are particularly affected. Services relying on this logic are at risk of unauthorized access. Version 25.6.7 fixes the vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/48xxx/CVE-2025-48952.json
- https://github.com/jokob-sk/NetAlertX/security/advisories/GHSA-4p4p-vq2v-9489
- https://nvd.nist.gov/vuln/detail/CVE-2025-48952
