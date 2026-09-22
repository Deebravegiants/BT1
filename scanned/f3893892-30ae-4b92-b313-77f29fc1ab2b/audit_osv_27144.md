# [H] Unhandled Exception Leading to Server Crash in danny-avila/librechat

## Summary
Severity: High
Advisory: CVE-2024-11169
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-11169
Type: osv

## Details
An unhandled exception in danny-avila/librechat version 3c94ff2 can lead to a server crash. The issue occurs when the fs module throws an exception while handling file uploads. An unauthenticated user can trigger this exception by sending a specially crafted request, causing the server to crash. The vulnerability is fixed in version 0.7.6.

## References
- https://huntr.com/bounties/754e1649-5612-4ba9-a533-06b46de5c4b5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/11xxx/CVE-2024-11169.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-11169
- https://github.com/danny-avila/librechat/commit/629be5c0ca2b332178524b4e3f6fac715aea8cc4
