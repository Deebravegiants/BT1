# [H] Insufficient Patch Leading to DoS in parisneo/lollms-webui

## Summary
Severity: High
Advisory: CVE-2025-1451
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2025-1451
Type: osv

## Details
A vulnerability in parisneo/lollms-webui v13 arises from the server's handling of multipart boundaries in file uploads. The server does not limit or validate the length of the boundary or the characters appended to it, allowing an attacker to craft requests with excessively long boundaries, leading to resource exhaustion and eventual denial of service (DoS). Despite an attempted patch in commit 483431bb, which blocked hyphen characters from being appended to the multipart boundary, the fix is insufficient. The server remains vulnerable if other characters (e.g., '4', 'a') are used instead of hyphens. This allows attackers to exploit the vulnerability using different characters, causing resource exhaustion and service unavailability.

## References
- https://huntr.com/bounties/63f5aea4-953b-4b38-9f10-3afe425be1d4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/1xxx/CVE-2025-1451.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-1451
