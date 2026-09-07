# [M] Symphony CMS XSS Vulnerabilities

## Summary
Severity: Medium
Advisory: GHSA-4c5w-qqfg-grf3
CVE: CVE-2015-8766
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-4c5w-qqfg-grf3
Type: github-advisory

## Affected
- Packagist: `symphonycms/symphony-2` — affected >=0 <2.6.4

## Details
Multiple cross-site scripting (XSS) vulnerabilities in `content/content.systempreferences.php` in Symphony CMS before 2.6.4 allow remote attackers to inject arbitrary web script or HTML via the (1) `email_sendmail[from_name]`, (2) `email_sendmail[from_address]`, (3) `email_smtp[from_name]`, (4) `email_smtp[from_address]`, (5) `email_smtp[host]`, (6) `email_smtp[port]`, (7) `jit_image_manipulation[trusted_external_sites]`, or (8) `maintenance_mode[ip_whitelist]` parameters to system/preferences.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-8766
- https://github.com/symphonycms/symphony-2/commit/651e150091c61fb60ad1dff2bc2166185a83d9d6
- https://github.com/symphonycms/symphony-2
- https://web.archive.org/web/20210321090853/https://cybersecurityworks.com/zerodays/cve-2015-8766-getsymphoney.html
- http://seclists.org/fulldisclosure/2015/Dec/60
- http://www.getsymphony.com/download/releases/version/2.6.4
