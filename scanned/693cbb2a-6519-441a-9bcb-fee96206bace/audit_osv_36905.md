# [C] CVE-2026-26747

## Summary
Severity: Critical
Advisory: CVE-2026-26747
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-02-20
Source: https://osv.dev/vulnerability/CVE-2026-26747
Type: osv

## Details
A Host Header Poisoning vulnerability exists in Monica 4.1.2 due to improper handling of the HTTP Host header in app/Providers/AppServiceProvider.php, combined with the default misconfiguration where the "app.force_url" is not set and default is "false". The application generates absolute URLs (such as those used in password reset emails) using the user-supplied Host header. This allows remote attackers to poison the password reset link sent to a victim,

## References
- https://github.com/hungnqdz/cve-research/blob/main/CVE-2026-26747.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26747.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-26747
- https://github.com/monicahq/monica
