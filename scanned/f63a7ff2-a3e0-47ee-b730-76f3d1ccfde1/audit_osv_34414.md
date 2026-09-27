# [M] Inadequate validation of SSO redirect credentials permits credential theft

## Summary
Severity: Medium
Advisory: CVE-2025-59480
CVSS: 6.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:N/A:N)
Published: 2025-11-13
Source: https://osv.dev/vulnerability/CVE-2025-59480
Type: osv

## Details
Mattermost Mobile Apps versions <=2.32.0 fail to verify that SSO redirect tokens originate from the trusted server, which allows a malicious Mattermost instance or on-path attacker to obtain user session credentials via crafted token-in-URL responses

## References
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59480.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-59480
