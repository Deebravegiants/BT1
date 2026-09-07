# [M] Formstone Vulnerable to Reflected XSS

## Summary
Severity: Medium
Advisory: GHSA-wc29-h54q-q8qx
CVE: CVE-2020-26768
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-wc29-h54q-q8qx
Type: github-advisory

## Affected
- npm: `formstone` — affected >=0 <1.4.17

## Details
Formstone <=1.4.16 is vulnerable to a Reflected Cross-Site Scripting (XSS) vulnerability caused by improper validation of user supplied input in the `upload-target.php` and `upload-chunked.php` files. A remote attacker could exploit this vulnerability using a specially crafted URL to execute a script in a victim's Web browser within the security context of the hosting Web site once the URL is clicked or visited. An attacker could use this vulnerability to steal the victim's cookie-based authentication credentials, force malware execution, user redirection and others.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-26768
- https://github.com/Formstone/Formstone/issues/286
- https://github.com/Formstone/Formstone/commit/b067f31f5f6a0acd3ade4fd6dccae6e3633caa02
