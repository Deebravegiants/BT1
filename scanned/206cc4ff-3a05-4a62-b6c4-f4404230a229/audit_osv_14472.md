# [H] CVE-2019-1003038

## Summary
Severity: High
Advisory: CVE-2019-1003038
Aliases: GHSA-99jc-v8pq-6qm4
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-03-08
Source: https://osv.dev/vulnerability/CVE-2019-1003038
Type: osv

## Details
An insufficiently protected credentials vulnerability exists in Jenkins Repository Connector Plugin 1.2.4 and earlier in src/main/java/org/jvnet/hudson/plugins/repositoryconnector/ArtifactDeployer.java, src/main/java/org/jvnet/hudson/plugins/repositoryconnector/Repository.java, src/main/java/org/jvnet/hudson/plugins/repositoryconnector/UserPwd.java that allows an attacker with local file system access or control of a Jenkins administrator's web browser (e.g. malicious extension) to retrieve the password stored in the plugin configuration.

## References
- http://www.securityfocus.com/bid/107476
- https://jenkins.io/security/advisory/2019-03-06/#SECURITY-958
