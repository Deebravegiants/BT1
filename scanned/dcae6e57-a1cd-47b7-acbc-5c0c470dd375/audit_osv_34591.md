# [H] CVE-2025-62291

## Summary
Severity: High
Advisory: CVE-2025-62291
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-16
Source: https://osv.dev/vulnerability/CVE-2025-62291
Type: osv

## Details
In the eap-mschapv2 plugin (client-side) in strongSwan before 6.0.3, a malicious EAP-MSCHAPv2 server can send a crafted message of size 6 through 8, and cause an integer underflow that potentially results in a heap-based buffer overflow.

## References
- https://github.com/strongswan/strongswan/commits/master/src/libcharon/plugins/eap_mschapv2
- https://lists.debian.org/debian-lts-announce/2025/11/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/62xxx/CVE-2025-62291.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-62291
- https://github.com/strongswan/strongswan/releases
- https://www.strongswan.org/blog/2025/10/27/strongswan-vulnerability-%28cve-2025-62291%29.html
