# [C] jsreport vulnerable to code injection

## Summary
Severity: Critical
Advisory: GHSA-g7rj-q722-245g
CVE: CVE-2023-2583
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-05-08
Source: https://github.com/advisories/GHSA-g7rj-q722-245g
Type: github-advisory

## Affected
- npm: `jsreport` — affected >=0 <3.11.3

## Details
jsreport prior to 3.11.3 had a version of vm2 vulnerable to CVE-2023-29017 hard coded in the package.json of the jsreport-core component. An attacker can use this vulnerability to obtain the authority of the jsreport playground server, or construct a malicious webpage/html file and send it to the user to attack the installed jsreport client.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-2583
- https://github.com/jsreport/jsreport/commit/afaff3804b34b38e959f5ae65f9e672088de13d7
- https://github.com/jsreport/jsreport
- https://github.com/jsreport/jsreport/releases/tag/3.11.3
- https://huntr.dev/bounties/397ea68d-1e28-44ff-b830-c8883d067d96
