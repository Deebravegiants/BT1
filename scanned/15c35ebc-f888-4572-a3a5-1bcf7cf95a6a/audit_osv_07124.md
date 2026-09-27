# [M] BIT-node-2021-44533

## Summary
Severity: Medium
Advisory: BIT-node-2021-44533
Aliases: BIT-node-min-2021-44533, CVE-2021-44533
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-node-2021-44533
Type: osv

## Affected
- Bitnami: `node` — affected >=17.0.0 <17.3.1

## Details
Node.js < 12.22.9, < 14.18.3, < 16.13.2, and < 17.3.1 did not handle multi-value Relative Distinguished Names correctly. Attackers could craft certificate subjects containing a single-value Relative Distinguished Name that would be interpreted as a multi-value Relative Distinguished Name, for example, in order to inject a Common Name that would allow bypassing the certificate subject verification.Affected versions of Node.js that do not accept multi-value Relative Distinguished Names and are thus not vulnerable to such attacks themselves. However, third-party code that uses node's ambiguous presentation of certificate subjects may be vulnerable.

## References
- https://hackerone.com/reports/1429694
- https://nodejs.org/en/blog/vulnerability/jan-2022-security-releases/
- https://security.netapp.com/advisory/ntap-20220325-0007/
- https://www.debian.org/security/2022/dsa-5170
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://nvd.nist.gov/vuln/detail/CVE-2021-44533
