# [H] Postiz App has a High-Severity SSRF Vulnerability via Next.js

## Summary
Severity: High
Advisory: GHSA-vj2p-7pgw-g2wf
CWE: CWE-1395, CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-vj2p-7pgw-g2wf
Type: github-advisory

## Affected
- npm: `postiz` — affected >=0

## Details
### Impact
A successful SSRF attack allows an attacker to:
- Bypass firewalls to scan and interact with internal network services/ports.
- Access sensitive cloud metadata services (e.g., AWS IMDS 169.254.169.254) to potentially leak instance credentials.
- Pivot into the internal network environment where Postiz is hosted.

### Workarounds
There are no workarounds known to this, please upgrade to Postiz version `v2.21.1`.

## References
- https://github.com/gitroomhq/postiz-app/security/advisories/GHSA-vj2p-7pgw-g2wf
- https://github.com/vercel/next.js/security/advisories/GHSA-fr5h-rqp8-mj6g
- https://nvd.nist.gov/vuln/detail/CVE-2024-34351
- https://github.com/gitroomhq/postiz-app
