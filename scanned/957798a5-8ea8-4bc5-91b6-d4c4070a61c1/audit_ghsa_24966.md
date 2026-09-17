# [M] Emails were sent to addresses not associated with actual users of Jenkins by Email Extension Plugin

## Summary
Severity: Medium
Advisory: GHSA-c8qr-vfjf-62q3
CVE: CVE-2017-2654
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-c8qr-vfjf-62q3
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:email-ext` — affected >=0 <2.57.1

## Details
jenkins-email-ext before version 2.57.1 is vulnerable to an Information Exposure. The Email Extension Plugins is able to send emails to a dynamically created list of users based on the changelogs, like authors of SCM changes since the last successful build. This could in some cases result in emails being sent to people who have no user account in Jenkins, and in rare cases even people who were not involved in whatever project was being built, due to some mapping based on the local-part of email addresses.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-2654
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-2654
- https://jenkins.io/security/advisory/2017-03-20
