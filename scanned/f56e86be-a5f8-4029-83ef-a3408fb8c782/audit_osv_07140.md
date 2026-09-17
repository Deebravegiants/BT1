# [H] BIT-node-2023-32004

## Summary
Severity: High
Advisory: BIT-node-2023-32004
Aliases: BIT-node-min-2023-32004, CVE-2023-32004
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-node-2023-32004
Type: osv

## Affected
- Bitnami: `node` — affected >=20.0.0 <20.5.1

## Details
A vulnerability has been discovered in Node.js version 20, specifically within the experimental permission model. This flaw relates to improper handling of Buffers in file system APIs causing a traversal path to bypass when verifying file permissions.

This vulnerability affects all users using the experimental permission model in Node.js 20.

Please note that at the time this CVE was issued, the permission model is an experimental feature of Node.js.

## References
- https://hackerone.com/reports/2038134
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/JQPELKG2LVTADSB7ME73AV4DXQK47PWK/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PBOZE2QZIBLFFTYWYN23FGKN6HULZ6HX/
- https://security.netapp.com/advisory/ntap-20230915-0009/
- https://nvd.nist.gov/vuln/detail/CVE-2023-32004
