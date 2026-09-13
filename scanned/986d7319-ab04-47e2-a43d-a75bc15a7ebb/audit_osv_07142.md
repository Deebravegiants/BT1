# [H] BIT-node-2023-32006

## Summary
Severity: High
Advisory: BIT-node-2023-32006
Aliases: BIT-node-min-2023-32006, CVE-2023-32006
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-node-2023-32006
Type: osv

## Affected
- Bitnami: `node` — affected >=19.0.0 <20.5.1

## Details
The use of `module.constructor.createRequire()` can bypass the policy mechanism and require modules outside of the policy.json definition for a given module.

This vulnerability affects all users using the experimental policy mechanism in all active release lines: 16.x, 18.x, and, 20.x.

Please note that at the time this CVE was issued, the policy is an experimental feature of Node.js.

## References
- https://hackerone.com/reports/2043807
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/JQPELKG2LVTADSB7ME73AV4DXQK47PWK/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PBOZE2QZIBLFFTYWYN23FGKN6HULZ6HX/
- https://security.netapp.com/advisory/ntap-20230915-0009/
- https://nvd.nist.gov/vuln/detail/CVE-2023-32006
