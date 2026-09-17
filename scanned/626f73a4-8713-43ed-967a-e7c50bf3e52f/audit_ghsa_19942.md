# [M] nadesiko3 allows remote attacker to inject invalid value to decodeURIComponent of nako3edit

## Summary
Severity: Medium
Advisory: GHSA-x2jx-w3wm-9p3p
CVE: CVE-2022-41777
CWE: CWE-703, CWE-755
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2022-12-05
Source: https://github.com/advisories/GHSA-x2jx-w3wm-9p3p
Type: github-advisory

## Affected
- npm: `nadesiko3` — affected >=0 <3.3.75

## Details
Nako3edit is the editor component of Nadeshiko 3, a programming language developed based on Japanese. Improper check or handling of exceptional conditions in Nako3edit v3.3.74 and earlier allows a remote attacker to inject an invalid value to decodeURIComponent of nako3edit, which may lead the server to crash.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-41777
- https://github.com/kujirahand/nadesiko3/issues/1325
- https://github.com/kujirahand/nadesiko3/issues/1347
- https://github.com/kujirahand/nadesiko3
- https://github.com/kujirahand/nadesiko3/releases/tag/3.3.75
- https://jvn.jp/en/jp/JVN56968681/index.html
