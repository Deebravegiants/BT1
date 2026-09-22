# [C] CVE-2020-1896

## Summary
Severity: Critical
Advisory: CVE-2020-1896
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-02-02
Source: https://osv.dev/vulnerability/CVE-2020-1896
Type: osv

## Details
A stack overflow vulnerability in Facebook Hermes 'builtin apply' prior to commit 86543ac47e59c522976b5632b8bf9a2a4583c7d2 (https://github.com/facebook/hermes/commit/86543ac47e59c522976b5632b8bf9a2a4583c7d2) allows attackers to potentially execute arbitrary code via crafted JavaScript. Note that this is only exploitable if the application using Hermes permits evaluation of untrusted JavaScript. Hence, most React Native applications are not affected.

## References
- https://www.facebook.com/security/advisories/cve-2020-1896
- https://github.com/facebook/hermes/commit/86543ac47e59c522976b5632b8bf9a2a4583c7d2
