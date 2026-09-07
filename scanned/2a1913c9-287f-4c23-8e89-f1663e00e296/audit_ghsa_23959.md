# [H] Codiad Vulnerable to PHP Magic Hash Vulnerability

## Summary
Severity: High
Advisory: GHSA-8fhh-hf9w-55p7
CVE: CVE-2020-23355
CWE: CWE-287, CWE-697
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-8fhh-hf9w-55p7
Type: github-advisory

## Affected
- Packagist: `codiad/codiad` — affected >=0

## Details
Codiad 2.8.4 `/componetns/user/class.user.php:Authenticate()` is vulnerable in magic hash authentication bypass. If encrypted or hash value for the passwords form certain formats of magic hash, e.g, `0e123`, another hash value `0e234[something]` can successfully authenticate.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-23355
- https://github.com/Codiad/Codiad/issues/1121
- https://github.com/Codiad/Codiad
- https://web.archive.org/web/20160722013412/https://www.whitehatsec.com/blog/magic-hashes
