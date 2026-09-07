# [C] Raneto v0.17.0 employs weak password complexity requirements

## Summary
Severity: Critical
Advisory: GHSA-7942-2fx8-qhpf
CVE: CVE-2022-35143
CWE: CWE-521
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-08-05
Source: https://github.com/advisories/GHSA-7942-2fx8-qhpf
Type: github-advisory

## Affected
- npm: `raneto` — affected >=0 <0.17.1

## Details
Raneto v0.17.0 employs weak password complexity requirements, allowing attackers to crack user passwords via brute-force attacks. Version 0.17.1 contains security mitigations for this and other vulnerabilities.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-35143
- https://github.com/ryanlelek/Raneto/pull/370
- https://github.com/ryanlelek/Raneto/commit/55e442c9bc67b845094e14ceb228e95c639595be
- https://cwe.mitre.org/data/definitions/521.html
- https://gainsec.com/2022/08/04/cve-2022-35142-cve-2022-35143-cve-2022-35144
- https://github.com/gilbitron/Raneto/releases
- https://github.com/ryanlelek/Raneto
- https://github.com/ryanlelek/Raneto/releases/tag/0.17.1
- http://raneto.com
