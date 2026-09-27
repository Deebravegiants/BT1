# [M] Zammad has a Server-side request forgery (SSRF) via webhooks

## Summary
Severity: Medium
Advisory: CVE-2026-34719
Aliases: GHSA-2vgc-vfh2-rw75
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:L/VI:N/VA:H/SC:L/SI:N/SA:H)
Published: 2026-04-08
Source: https://osv.dev/vulnerability/CVE-2026-34719
Type: osv

## Details
Zammad is a web based open source helpdesk/customer support system. Prior to 7.0.1 and 6.5.4, the webhook model was missing a proper validation for loop back addresses, or link-local addresses — only the URL scheme (HTTP/HTTPS) as well as the hostname was checked. This could end up in retrieving confidential metadata of cloud/hosting providers. The existing check is now extended and is applied when configuring webhooks as well as triggering webhook jobs. This vulnerability is fixed in 7.0.1 and 6.5.4.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34719.json
- https://github.com/zammad/zammad/security/advisories/GHSA-2vgc-vfh2-rw75
- https://nvd.nist.gov/vuln/detail/CVE-2026-34719
