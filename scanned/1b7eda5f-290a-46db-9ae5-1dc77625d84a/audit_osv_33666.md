# [H] Apache HertzBeat (incubating): Jmx JNDI injection vulnerability

## Summary
Severity: High
Advisory: CVE-2025-48208
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-09
Source: https://osv.dev/vulnerability/CVE-2025-48208
Type: osv

## Details
Improper Neutralization of Special Elements used in an LDAP Query ('LDAP Injection') vulnerability in Apache HertzBeat .












The attacker needs to have an authenticated account with access, and the attack can only be triggered by crafting custom commands. A successful attack would result in arbitrary script execution.

This issue affects Apache HertzBeat: through 1.7.2.

Users are recommended to upgrade to version [1.7.3], which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2025/09/06/5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/48xxx/CVE-2025-48208.json
- https://lists.apache.org/thread/3zrr3oo67pxxx7wgzj80kglltfshngn2
- https://nvd.nist.gov/vuln/detail/CVE-2025-48208
