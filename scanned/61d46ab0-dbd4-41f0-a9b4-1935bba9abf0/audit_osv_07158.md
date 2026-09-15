# [H] BIT-node-2024-36138

## Summary
Severity: High
Advisory: BIT-node-2024-36138
Aliases: BIT-node-min-2024-36138, CVE-2024-36138
Ecosystem: Bitnami
Published: 2024-09-10
Source: https://osv.dev/vulnerability/BIT-node-2024-36138
Type: osv

## Affected
- Bitnami: `node` — affected >=21.0.0 <22.4.1

## Details
Bypass incomplete fix of CVE-2024-27980, that arises from improper handling of batch files with all possible extensions on Windows via child_process.spawn / child_process.spawnSync. A malicious command line argument can inject arbitrary commands and achieve code execution even if the shell option is not enabled.

## References
- https://nodejs.org/en/blog/vulnerability/july-2024-security-releases
- https://security.netapp.com/advisory/ntap-20241108-0010/
- https://nvd.nist.gov/vuln/detail/CVE-2024-36138
- https://www.oracle.com/security-alerts/cpuoct2024.html
