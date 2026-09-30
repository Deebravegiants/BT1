# [M] ThinkDashboard: Blind Server-Side Request Forgery (SSRF) vulnerability in /api/ping Endpoint

## Summary
Severity: Medium
Advisory: CVE-2025-64327
Aliases: GHSA-p52r-qq3j-8p78
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-11-06
Source: https://osv.dev/vulnerability/CVE-2025-64327
Type: osv

## Details
ThinkDashboard is a self-hosted bookmark dashboard built with Go and vanilla JavaScript. Versions 0.6.7 and below contain a Blind Server-Side Request Forgery (SSRF) vulnerability, in its `/api/ping?url= endpoint`. This allows an attacker to make arbitrary requests to internal or external hosts. This can include discovering ports open on the local machine, hosts on the local network, and ports open on the hosts on the internal network. This issue is fixed in version 0.6.8.

## References
- https://github.com/MatiasDesuu/ThinkDashboard/releases/tag/0.6.8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64327.json
- https://github.com/MatiasDesuu/ThinkDashboard/security/advisories/GHSA-p52r-qq3j-8p78
- https://nvd.nist.gov/vuln/detail/CVE-2025-64327
- https://github.com/MatiasDesuu/ThinkDashboard/commit/16976263b22a4b0526b2c7c30294cc099258edae
