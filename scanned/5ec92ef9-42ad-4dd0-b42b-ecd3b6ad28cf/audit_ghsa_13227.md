# [H] Non-constant time nonce comparison in Jenkins Microsoft Entra ID (previously Azure AD) Plugin

## Summary
Severity: High
Advisory: GHSA-hj7p-h74j-6gxj
CVE: CVE-2023-41935
CWE: CWE-697
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-09-06
Source: https://github.com/advisories/GHSA-hj7p-h74j-6gxj
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:azure-ad` — affected >=378.380.v545b <397.v907382dd9b
- Maven: `org.jenkins-ci.plugins:azure-ad` — affected >=0 <378.vd6e2874a

## Details
Jenkins Azure AD Plugin 396.v86ce29279947 and earlier, except 378.380.v545b_1154b_3fb_, uses a non-constant time comparison function when checking whether the provided and expected CSRF protection nonce are equal, potentially allowing attackers to use statistical methods to obtain a valid nonce.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-41935
- https://www.jenkins.io/security/advisory/2023-09-06/#SECURITY-3227
- http://www.openwall.com/lists/oss-security/2023/09/06/9
