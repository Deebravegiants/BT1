# [H] Raneto Denial of Service via crafted payload injected into `Search` parameter

## Summary
Severity: High
Advisory: GHSA-xxc2-j7jj-6g5m
CVE: CVE-2022-35142
CWE: CWE-287
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-08-05
Source: https://github.com/advisories/GHSA-xxc2-j7jj-6g5m
Type: github-advisory

## Affected
- npm: `raneto` — affected >=0 <0.17.1

## Details
An issue in Renato v0.17.0 allows attackers to cause a Denial of Service (DoS) via a crafted payload injected into the `Search` parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-35142
- https://github.com/ryanlelek/Raneto/issues/368
- https://github.com/ryanlelek/Raneto/pull/370
- https://cwe.mitre.org/data/definitions/703.html
- https://gainsec.com/2022/08/04/cve-2022-35142-cve-2022-35143-cve-2022-35144
- https://github.com/gilbitron/Raneto/releases
- https://github.com/ryanlelek/Raneto
- https://github.com/ryanlelek/Raneto/releases/tag/0.17.1
- http://raneto.com
