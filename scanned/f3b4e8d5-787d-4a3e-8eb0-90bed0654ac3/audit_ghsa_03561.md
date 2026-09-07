# [M] Cross-site scripting (XSS) in Apache Velocity Tools

## Summary
Severity: Medium
Advisory: GHSA-fh63-4r66-jc7v
CVE: CVE-2020-13959
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-03-12
Source: https://github.com/advisories/GHSA-fh63-4r66-jc7v
Type: github-advisory

## Affected
- Maven: `org.apache.velocity.tools:velocity-tools-parent` — affected >=0 <3.1
- Maven: `org.apache.velocity:velocity-tools` — affected >=0

## Details
The default error page for VelocityView in Apache Velocity Tools prior to 3.1 reflects back the vm file that was entered as part of the URL. An attacker can set an XSS payload file as this vm file in the URL which results in this payload being executed. XSS vulnerabilities allow attackers to execute arbitrary JavaScript in the context of the attacked website and the attacked user. This can be abused to steal session cookies, perform requests in the name of the victim or for phishing attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13959
- https://lists.apache.org/thread.html/r6802a38c3041059e763a1aadd7b37fe95de75408144b5805e29b84e3%40%3Cuser.velocity.apache.org%3E
- https://lists.apache.org/thread.html/r6802a38c3041059e763a1aadd7b37fe95de75408144b5805e29b84e3@%3Cuser.velocity.apache.org%3E
- https://lists.apache.org/thread.html/r97edad0655770342d2d36620fb1de50b142fcd6c4f5c53dd72ca41d7@%3Cuser.velocity.apache.org%3E
- https://lists.apache.org/thread.html/rb042f3b0090e419cc9f5a3d32cf0baff283ccd6fcb1caea61915d6b6@%3Ccommits.velocity.apache.org%3E
- https://lists.apache.org/thread.html/rf9868c564cff7adfd5283563f2309b93b3e496354a211a57503b2f72@%3Cannounce.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2021/03/msg00021.html
- https://security.gentoo.org/glsa/202107-52
- http://www.openwall.com/lists/oss-security/2021/03/10/2
