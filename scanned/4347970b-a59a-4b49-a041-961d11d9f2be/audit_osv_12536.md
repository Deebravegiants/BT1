# [C] CVE-2018-12678

## Summary
Severity: Critical
Advisory: CVE-2018-12678
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-22
Source: https://osv.dev/vulnerability/CVE-2018-12678
Type: osv

## Details
Portainer before 1.18.0 supports unauthenticated requests to the websocket endpoint with an unvalidated id query parameter for the /websocket/exec endpoint, which allows remote attackers to bypass intended access restrictions or conduct SSRF attacks.

## References
- https://github.com/portainer/portainer/releases/tag/1.18.0
- https://github.com/portainer/portainer/pull/1979
