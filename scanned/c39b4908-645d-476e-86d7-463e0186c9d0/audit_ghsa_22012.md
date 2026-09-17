# [M] Agent-to-controller security bypass in Jenkins HashiCorp Vault Plugin allows reading arbitrary files

## Summary
Severity: Medium
Advisory: GHSA-2587-w93g-63m2
CVE: CVE-2022-25197
CWE: CWE-693
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-02-16
Source: https://github.com/advisories/GHSA-2587-w93g-63m2
Type: github-advisory

## Affected
- Maven: `com.datapipe.jenkins.plugins:hashicorp-vault-plugin` — affected >=0 <351.vdb_f83a_1c6a_9d

## Details
Jenkins HashiCorp Vault Plugin 336.v182c0fbaaeb7 and earlier implements functionality that allows agent processes to read arbitrary files on the Jenkins controller file system.

This allows attackers able to control agent processes to read arbitrary files on the Jenkins controller file system.

This vulnerability is only exploitable in Jenkins 2.318 and earlier, LTS 2.303.2 and earlier. See the [LTS upgrade guide](https://www.jenkins.io/doc/upgrade-guide/2.303/#upgrading-to-jenkins-lts-2-303-3).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25197
- https://github.com/jenkinsci/hashicorp-vault-plugin/commit/c564958154e5b2eccb2423b0aaabd01b928f71fc
- https://github.com/jenkinsci/hashicorp-vault-plugin
- https://github.com/jenkinsci/hashicorp-vault-plugin/releases/tag/351.vdb_f83a_1c6a_9d
- https://www.jenkins.io/security/advisory/2022-02-15/#SECURITY-2521
