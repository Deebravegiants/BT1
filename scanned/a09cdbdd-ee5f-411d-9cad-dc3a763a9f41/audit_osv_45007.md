# [M] Mattermost Desktop App crashes when malformed arguments are provided to some exposed IPC methods

## Summary
Severity: Medium
Advisory: CVE-2026-9602
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-17
Source: https://osv.dev/vulnerability/CVE-2026-9602
Type: osv

## Details
Mattermost Desktop App versions <=6.2 6.0.2 5.6.13.0 fail to validate payloads sent from the Mattermost Web App to the Desktop App which allows a malicious server owner to crash the Mattermost Desktop App via changing the payload of a method to a malformed one. Mattermost Advisory ID: MMSA-2026-00678

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/9xxx/CVE-2026-9602.json
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2026-9602
