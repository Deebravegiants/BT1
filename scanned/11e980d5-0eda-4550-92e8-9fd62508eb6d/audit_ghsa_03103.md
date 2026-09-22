# [H] Prototype Pollution in jquery-deparam

## Summary
Severity: High
Advisory: GHSA-xg68-chx2-253g
CVE: CVE-2021-20087
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-24
Source: https://github.com/advisories/GHSA-xg68-chx2-253g
Type: github-advisory

## Affected
- npm: `jquery-deparam` — affected >=0

## Details
Improperly Controlled Modification of Object Prototype Attributes ('Prototype Pollution') in jquery-deparam allows a malicious user to inject properties into Object.prototype.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-20087
- https://github.com/BlackFan/client-side-prototype-pollution/blob/master/pp/jquery-deparam.md
- https://github.com/RetireJS/retire.js/blob/6da45fcb6a3425e55ee8181b2ac35168879bf086/repository/jsrepository-master.json#L824-L842
