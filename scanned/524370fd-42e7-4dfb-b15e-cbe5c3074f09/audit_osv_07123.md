# [M] BIT-node-2021-44532

## Summary
Severity: Medium
Advisory: BIT-node-2021-44532
Aliases: BIT-node-min-2021-44532, CVE-2021-44532
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-node-2021-44532
Type: osv

## Affected
- Bitnami: `node` — affected >=17.0.0 <17.3.1

## Details
Node.js < 12.22.9, < 14.18.3, < 16.13.2, and < 17.3.1 converts SANs (Subject Alternative Names) to a string format. It uses this string to check peer certificates against hostnames when validating connections. The string format was subject to an injection vulnerability when name constraints were used within a certificate chain, allowing the bypass of these name constraints.Versions of Node.js with the fix for this escape SANs containing the problematic characters in order to prevent the injection. This behavior can be reverted through the --security-revert command-line option.

## References
- https://hackerone.com/reports/1429694
- https://nodejs.org/en/blog/vulnerability/jan-2022-security-releases/
- https://security.netapp.com/advisory/ntap-20220325-0007/
- https://www.debian.org/security/2022/dsa-5170
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://nvd.nist.gov/vuln/detail/CVE-2021-44532
