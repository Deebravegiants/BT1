# [M] Jenkins vulnerable to UDP amplification reflection attack

## Summary
Severity: Medium
Advisory: GHSA-gpxv-776p-7gc7
CVE: CVE-2020-2100
CWE: CWE-406
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:L (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-gpxv-776p-7gc7
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.204.2
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.205 <2.219

## Details
Jenkins 2.218 and earlier, LTS 2.204.1 and earlier supports two network discovery services (UDP multicast/broadcast and DNS multicast) by default.

The UDP multicast/broadcast service can be used in an amplification reflection attack, as very few bytes sent to the respective endpoint result in much larger responses: A single byte request to this service would respond with more than 100 bytes of Jenkins metadata which could be used in a DDoS attack on a Jenkins controller. Within the same network, spoofed UDP packets could also be sent to make two Jenkins controllers go into an infinite loop of replies to one another, thus causing a denial of service.

Jenkins 2.219, LTS 2.204.2 now disables both UDP multicast/broadcast and DNS multicast by default.

Administrators that need these features can re-enable them again by setting the system property `hudson.DNSMultiCast.disabled` to `false` (for DNS multicast) or the system property `hudson.udp` to `33848`, or another port (for UDP broadcast/multicast). These are the same system properties that controlled whether these features were enabled in the past, so any instances explicitly enabling these features by setting these system properties will continue to have them enabled.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2100
- https://github.com/jenkinsci/jenkins/commit/cd28a6d9347228b03da0e45653e23032342c2a36
- https://access.redhat.com/errata/RHBA-2020:0402
- https://access.redhat.com/errata/RHBA-2020:0675
- https://access.redhat.com/errata/RHSA-2020:0681
- https://access.redhat.com/errata/RHSA-2020:0683
- https://github.com/jenkinsci/jenkins
- https://jenkins.io/security/advisory/2020-01-29/#SECURITY-1641
- http://www.openwall.com/lists/oss-security/2020/01/29/1
