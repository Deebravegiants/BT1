# [H] File upload restriction bypass in Zenario CMS

## Summary
Severity: High
Advisory: GHSA-6r86-2jm9-9mh4
CVE: CVE-2022-23043
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-25
Source: https://github.com/advisories/GHSA-6r86-2jm9-9mh4
Type: github-advisory

## Affected
- Packagist: `tribalsystems/zenario` — affected >=0 <9.2.55826

## Details
Zenario CMS 9.2 allows an authenticated admin user to bypass the file upload restriction by creating a new 'File/MIME Types' using the '.phar' extension. Then an attacker can upload a malicious file, intercept the request and change the extension to '.phar' in order to run commands on the server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-23043
- https://github.com/TribalSystems/Zenario/commit/f0682d22688d9921dc0dfd6e858900ebf2706f19
- https://fluidattacks.com/advisories/simone
- https://github.com/TribalSystems/Zenario
- https://github.com/TribalSystems/Zenario/releases/tag/9.2.55826
