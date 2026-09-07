# [H] October CMS CSRF 

## Summary
Severity: High
Advisory: GHSA-vm6r-4p4v-232x
CVE: CVE-2017-16244
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-vm6r-4p4v-232x
Type: github-advisory

## Affected
- Packagist: `october/october` — affected >=0 <1.0.427

## Details
Cross-Site Request Forgery exists in OctoberCMS 1.0.426 (aka Build 426) due to improper validation of CSRF tokens for postback handling, allowing an attacker to successfully take over the victim's account. The attack bypasses a protection mechanism involving X-CSRF headers and CSRF tokens via a certain _handler postback variable.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16244
- https://github.com/octobercms/october/commit/4a6e0e1e0e2c3facebc17e0db38c5b4d4cb05bd0
- https://github.com/octobercms/october
- https://www.exploit-db.com/exploits/43106
