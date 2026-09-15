# [M] ts-fns has prototype pollution vulnerability

## Summary
Severity: Medium
Advisory: GHSA-g7wq-wggw-vmhg
CVE: CVE-2025-57351
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:L/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-24
Source: https://github.com/advisories/GHSA-g7wq-wggw-vmhg
Type: github-advisory

## Affected
- npm: `ts-fns` — affected >=0

## Details
A prototype pollution vulnerability exists in the ts-fns package versions prior to 13.0.7, where insufficient validation of user-provided keys in the assign function allows attackers to manipulate the Object.prototype chain. By leveraging this flaw, adversaries may inject arbitrary properties into the global object's prototype, potentially leading to application crashes, unexpected code execution behaviors, or bypasses of security-critical validation logic dependent on prototype integrity. The vulnerability stems from improper handling of deep property assignment operations within the library's public API functions. This issue remains unaddressed in the latest available version.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-57351
- https://github.com/tangshuang/ts-fns/issues/36
- https://github.com/VulnSageAgent/PoCs/tree/main/JavaScript/prototype-pollution/CVE-2025-57351
- https://github.com/tangshuang/ts-fns
