# [M] CVE-2023-28359

## Summary
Severity: Medium
Advisory: CVE-2023-28359
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2023-05-11
Source: https://osv.dev/vulnerability/CVE-2023-28359
Type: osv

## Details
A NoSQL injection vulnerability has been identified in the listEmojiCustom method call within Rocket.Chat. This can be exploited by unauthenticated users when there is at least one custom emoji uploaded to the Rocket.Chat instance. The vulnerability causes a delay in the server response, with the potential for limited impact.

## References
- https://hackerone.com/reports/1757676
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/28xxx/CVE-2023-28359.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-28359
