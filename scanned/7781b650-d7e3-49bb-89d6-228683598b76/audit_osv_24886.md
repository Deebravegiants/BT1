# [M] Lack of URL normalization allows rendering previews for disallowed domains

## Summary
Severity: Medium
Advisory: CVE-2023-2808
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2023-05-29
Source: https://osv.dev/vulnerability/CVE-2023-2808
Type: osv

## Details
Mattermost fails to normalize UTF confusable characters when determining if a preview should be generated for a hyperlink, allowing an attacker to trigger link preview on a disallowed domain using a specially crafted link.

## References
- https://mattermost.com/security-updates/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/2xxx/CVE-2023-2808.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-2808
