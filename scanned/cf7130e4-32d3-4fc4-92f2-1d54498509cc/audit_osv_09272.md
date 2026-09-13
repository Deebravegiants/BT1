# [C] CVE-2016-9299

## Summary
Severity: Critical
Advisory: CVE-2016-9299
Aliases: GHSA-2x9h-h3c4-wqqh
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-01-12
Source: https://osv.dev/vulnerability/CVE-2016-9299
Type: osv

## Details
The remoting module in Jenkins before 2.32 and LTS before 2.19.3 allows remote attackers to execute arbitrary code via a crafted serialized Java object, which triggers an LDAP query to a third-party server.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZW2KUKYLNLVDB7STLHLYALCUFLEGCRM6/
- http://www.openwall.com/lists/oss-security/2016/11/12/4
- http://www.openwall.com/lists/oss-security/2016/11/14/9
- http://www.securityfocus.com/bid/94281
- http://www.slideshare.net/codewhitesec/java-deserialization-vulnerabilities-the-forgotten-bug-class-deepsec-edition
- https://groups.google.com/forum/#%21original/jenkinsci-advisories/-fc-w9tNEJE/GRvEzWoJBgAJ
- https://groups.google.com/forum/#%21original/jenkinsci-advisories/-fc-w9tNEJE/LZ7EOS0fBgAJ
- https://wiki.jenkins-ci.org/display/SECURITY/Jenkins+Security+Advisory+2016-11-16
- https://www.cloudbees.com/jenkins-security-advisory-2016-11-16
- https://www.exploit-db.com/exploits/44642/
