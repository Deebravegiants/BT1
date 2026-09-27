# [H] Using malformed From header can forge identity with ";" or NULL in name portion

## Summary
Severity: High
Advisory: CVE-2025-47779
Aliases: GHSA-2grh-7mhv-fcfw
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:N)
Published: 2025-05-22
Source: https://osv.dev/vulnerability/CVE-2025-47779
Type: osv

## Details
Asterisk is an open-source private branch exchange (PBX). Prior to versions 18.26.2, 20.14.1, 21.9.1, and 22.4.1 of Asterisk and versions 18.9-cert14 and 20.7-cert5 of certified-asterisk, SIP requests of the type MESSAGE (RFC 3428) authentication do not get proper alignment. An authenticated attacker can spoof any user identity to send spam messages to the user with their authorization token. Abuse of this security issue allows authenticated attackers to send fake chat messages can be spoofed to appear to come from trusted entities. Even administrators who follow Security best practices and Security Considerations can be impacted. Therefore, abuse can lead to spam and enable social engineering, phishing and similar attacks. Versions 18.26.2, 20.14.1, 21.9.1, and 22.4.1 of Asterisk and versions 18.9-cert14 and 20.7-cert5 of certified-asterisk fix the issue.

## References
- https://github.com/asterisk/asterisk/blob/master/configs/samples/pjsip.conf.sample
- https://lists.debian.org/debian-lts-announce/2025/06/msg00003.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/47xxx/CVE-2025-47779.json
- https://github.com/asterisk/asterisk/security/advisories/GHSA-2grh-7mhv-fcfw
- https://nvd.nist.gov/vuln/detail/CVE-2025-47779
