# [M] Mattermost allows external websites to open within the app, exposing preload functionality to non-trusted sites.

## Summary
Severity: Medium
Advisory: CVE-2026-1628
CVSS: 4.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N)
Published: 2026-03-02
Source: https://osv.dev/vulnerability/CVE-2026-1628
Type: osv

## Details
Mattermost Desktop App versions <=5.13.3 fail to attach listeners restricting navigation to external sites within the Mattermost app which allows a malicious server to expose preload script functionality to untrusted servers via having a user open an external link in their Mattermost server. Mattermost Advisory ID: MMSA-2026-00596

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/1xxx/CVE-2026-1628.json
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2026-1628
