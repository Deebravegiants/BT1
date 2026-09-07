# [M] Passwords stored in plain text by Jenkins Jabber (XMPP) notifier and control Plugin

## Summary
Severity: Medium
Advisory: GHSA-79r5-rhrw-7pvh
CVE: CVE-2021-21634
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-79r5-rhrw-7pvh
Type: github-advisory

## Affected
- Maven: `org.jvnet.hudson.plugins:jabber` — affected >=0 <1.42

## Details
Jenkins Jabber (XMPP) notifier and control Plugin 1.41 and earlier stores passwords unencrypted in its global configuration file `hudson.plugins.jabber.im.transport.JabberPublisher.xml` on the Jenkins controller as part of its configuration.

These passwords can be viewed by users with access to the Jenkins controller file system.

Jenkins Jabber (XMPP) notifier and control Plugin 1.42 stores passwords encrypted once its configuration is saved again.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21634
- https://github.com/jenkinsci/jabber-plugin/commit/67882cfd189d6d05ad39e043edbfbf079dc37677
- https://github.com/jenkinsci/jabber-plugin
- https://www.jenkins.io/security/advisory/2021-03-30/#SECURITY-2162
- http://www.openwall.com/lists/oss-security/2021/03/30/1
