# [M] Cross-site Scripting in pekeupload

## Summary
Severity: Medium
Advisory: GHSA-89q5-mj78-pw5w
CVE: CVE-2021-23673
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-12-02
Source: https://github.com/advisories/GHSA-89q5-mj78-pw5w
Type: github-advisory

## Affected
- npm: `pekeupload` — affected >=0

## Details
This affects all versions of package pekeupload. If an attacker induces a user to upload a file whose name contains javascript code, the javascript code will be executed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23673
- https://github.com/moxiecode/plupload
- https://github.com/moxiecode/plupload/blob/120cc0b5dd3373d7181fd11b06ac2557c890d3f0/js/jquery.plupload.queue/jquery.plupload.queue.js%23L226
- https://snyk.io/vuln/SNYK-JS-PEKEUPLOAD-1584360
