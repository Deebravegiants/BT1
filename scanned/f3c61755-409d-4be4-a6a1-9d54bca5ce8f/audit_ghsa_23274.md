# [M] Jenkins Subversion Plugin Stores Credentials with Base64 Encoding

## Summary
Severity: Medium
Advisory: GHSA-c4fr-gx5w-8qf2
CVE: CVE-2013-6372
CWE: CWE-326
Ecosystem: Maven
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-c4fr-gx5w-8qf2
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:subversion` — affected >=0 <1.54

## Details
The Subversion plugin before 1.54 for Jenkins stores credentials using base64 encoding, which allows local users to obtain passwords and SSH private keys by reading a subversion.credentials file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-6372
- https://github.com/jenkinsci/subversion-plugin/commit/7d4562d6f7e40de04bbe29577b51c79f07d05ba6
- https://access.redhat.com/errata/RHBA-2014:1630
- https://access.redhat.com/security/cve/CVE-2013-6372
- https://bugzilla.redhat.com/show_bug.cgi?id=1032391
- https://github.com/jenkinsci/subversion-plugin
- https://wiki.jenkins-ci.org/display/SECURITY/Jenkins+Security+Advisory+2013-11-20
