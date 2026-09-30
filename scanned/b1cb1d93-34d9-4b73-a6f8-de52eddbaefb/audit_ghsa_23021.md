# [M] Jenkins Self-Organizing Swarm Plug-in Modules Plugin XXE vulnerability via UDP broadcast response

## Summary
Severity: Medium
Advisory: GHSA-w898-3ph8-5pgm
CVE: CVE-2019-10309
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.0/AV:A/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:L (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-w898-3ph8-5pgm
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:swarm` — affected >=0

## Details
Jenkins Swarm Plugin allows clients to auto-discover Jenkins instances on the same network through a UDP discovery request. Responses to this request are XML documents.

Swarm Plugin does not configure the XML parser in a way that would prevent XML External Entity (XXE) processing. This allows unauthenticated attackers on the same network to have Swarm clients parse a maliciously crafted XML response that uses external entities to read arbitrary files from the Swarm client or denial-of-service attacks.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10309
- https://jenkins.io/security/advisory/2019-04-30/#SECURITY-1252
- https://web.archive.org/web/20200227073756/http://www.securityfocus.com/bid/108159
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2019-0783
- http://www.openwall.com/lists/oss-security/2019/04/30/5
