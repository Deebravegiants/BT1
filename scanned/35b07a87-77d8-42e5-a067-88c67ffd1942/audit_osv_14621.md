# [M] CVE-2019-10322

## Summary
Severity: Medium
Advisory: CVE-2019-10322
Aliases: GHSA-gxm5-jrrf-5c4v
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2019-05-31
Source: https://osv.dev/vulnerability/CVE-2019-10322
Type: osv

## Details
A missing permission check in Jenkins Artifactory Plugin 3.2.2 and earlier in ArtifactoryBuilder.DescriptorImpl#doTestConnection allowed users with Overall/Read access to connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

## References
- http://www.openwall.com/lists/oss-security/2019/05/31/2
- http://www.securityfocus.com/bid/108540
- https://jenkins.io/security/advisory/2019-05-31/#SECURITY-1015%20%281%29
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2019-0787
