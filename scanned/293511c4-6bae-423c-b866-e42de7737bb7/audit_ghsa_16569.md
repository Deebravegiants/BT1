# [M] Jenkins Git server Plugin does not perform a permission check

## Summary
Severity: Medium
Advisory: GHSA-xh9c-vcf9-h94m
CVE: CVE-2024-34146
CWE: CWE-269
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-05-02
Source: https://github.com/advisories/GHSA-xh9c-vcf9-h94m
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:git-server` — affected >=0 <117.veb

## Details
Jenkins Git server Plugin 114.v068a_c7cc2574 and earlier does not perform a permission check for read access to a Git repository over SSH.

This allows attackers with a previously configured SSH public key but lacking Overall/Read permission to access Git repositories.

Git server Plugin 117.veb_68868fa_027 requires Overall/Read permission to access Git repositories over SSH.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-34146
- https://www.jenkins.io/security/advisory/2024-05-02/#SECURITY-3342
- http://www.openwall.com/lists/oss-security/2024/05/02/3
