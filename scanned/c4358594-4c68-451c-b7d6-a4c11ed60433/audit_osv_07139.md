# [M] BIT-node-2023-32003

## Summary
Severity: Medium
Advisory: BIT-node-2023-32003
Aliases: BIT-node-min-2023-32003, CVE-2023-32003
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-node-2023-32003
Type: osv

## Affected
- Bitnami: `node` — affected >=20.0.0 <20.5.1

## Details
`fs.mkdtemp()` and `fs.mkdtempSync()` can be used to bypass the permission model check using a path traversal attack. This flaw arises from a missing check in the fs.mkdtemp() API and the impact is a malicious actor could create an arbitrary directory.

This vulnerability affects all users using the experimental permission model in Node.js 20.

Please note that at the time this CVE was issued, the permission model is an experimental feature of Node.js.

## References
- https://hackerone.com/reports/2037887
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/JQPELKG2LVTADSB7ME73AV4DXQK47PWK/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PBOZE2QZIBLFFTYWYN23FGKN6HULZ6HX/
- https://security.netapp.com/advisory/ntap-20230915-0009/
- https://nvd.nist.gov/vuln/detail/CVE-2023-32003
