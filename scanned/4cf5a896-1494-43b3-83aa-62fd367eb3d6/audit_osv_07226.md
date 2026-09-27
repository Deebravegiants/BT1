# [C] BIT-openfire-2021-45967

## Summary
Severity: Critical
Advisory: BIT-openfire-2021-45967
Aliases: CVE-2021-45967
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-openfire-2021-45967
Type: osv

## Affected
- Bitnami: `openfire` — affected >=0 <4.5.0, >=4.5.0

## Details
An issue was discovered in Pascom Cloud Phone System before 7.20.x. A configuration error between NGINX and a backend Tomcat server leads to a path traversal in the Tomcat server, exposing unintended endpoints.

## References
- https://kerbit.io/research/read/blog/4
- https://tutorialboy24.blogspot.com/2022/03/the-story-of-3-bugs-that-lead-to.html
- https://www.pascom.net/doc/en/release-notes/
- https://www.pascom.net/doc/en/release-notes/pascom19/
