# [M] CVE-2021-3152

## Summary
Severity: Medium
Advisory: CVE-2021-3152
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2021-01-26
Source: https://osv.dev/vulnerability/CVE-2021-3152
Type: osv

## Details
Home Assistant before 2021.1.3 does not have a protection layer that can help to prevent directory-traversal attacks against custom integrations. NOTE: the vendor's perspective is that the vulnerability itself is in custom integrations written by third parties, not in Home Assistant; however, Home Assistant does have a security update that is worthwhile in addressing this situation

## References
- https://www.home-assistant.io/blog/2021/01/14/security-bulletin/
- https://www.home-assistant.io/blog/2021/01/22/security-disclosure/
