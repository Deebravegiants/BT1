# [H] High severity vulnerability that affects electron

## Summary
Severity: High
Advisory: GHSA-gvcj-pfq2-wxj7
CVE: CVE-2016-1202
CWE: CWE-426
Ecosystem: npm
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-gvcj-pfq2-wxj7
Type: github-advisory

## Affected
- npm: `electron` — affected >=0 <0.33.5

## Details
Untrusted search path vulnerability in Atom Electron before 0.33.5 allows local users to gain privileges via a Trojan horse Node.js module in a parent directory of a directory named on a require line.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-1202
- https://github.com/electron/electron/pull/2976
- https://github.com/electron/electron/commit/9a2e2b365d061ec10cd861391fd5b1344af7194d
- https://github.com/advisories/GHSA-gvcj-pfq2-wxj7
- https://github.com/electron/electron
- http://jvn.jp/en/jp/JVN00324715/index.html
- http://jvndb.jvn.jp/jvndb/JVNDB-2016-000054
