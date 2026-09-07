# [H] Jenkins Docker Swarm Plugin stored cross-site scripting vulnerability

## Summary
Severity: High
Advisory: GHSA-v9rw-hjr3-426h
CVE: CVE-2023-40350
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-08-16
Source: https://github.com/advisories/GHSA-v9rw-hjr3-426h
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:docker-swarm` — affected >=0

## Details
Jenkins Docker Swarm Plugin processes Docker responses to generate the Docker Swarm Dashboard view.

Docker Swarm Plugin 1.11 and earlier does not escape values returned from Docker before inserting them into the Docker Swarm Dashboard view. This results in a stored cross-site scripting (XSS) vulnerability exploitable by attackers able to control responses from Docker.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-40350
- https://www.jenkins.io/security/advisory/2023-08-16/#SECURITY-2811
- http://www.openwall.com/lists/oss-security/2023/08/16/3
