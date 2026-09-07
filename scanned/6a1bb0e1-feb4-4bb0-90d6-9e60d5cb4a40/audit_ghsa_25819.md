# [H] Unhandled case in node-lmdb

## Summary
Severity: High
Advisory: GHSA-32j9-6qqm-mq9g
CVE: CVE-2022-21164
CWE: CWE-241, CWE-703
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-03-17
Source: https://github.com/advisories/GHSA-32j9-6qqm-mq9g
Type: github-advisory

## Affected
- npm: `node-lmdb` — affected >=0 <0.9.7

## Details
The package node-lmdb before 0.9.7 is vulnerable to Denial of Service (DoS) when defining a non-invokable `ToString` value, which will cause a crash during type check.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-21164
- https://github.com/Venemo/node-lmdb/commit/97760104c0fd311206b88aecd91fa1f59fe2b85a
- https://github.com/Venemo/node-lmdb
- https://snyk.io/vuln/SNYK-JS-NODELMDB-2400723
