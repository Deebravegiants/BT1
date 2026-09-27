# [M] LinkAce has SSRF via CheckLinksCommand - Link URL Update Bypasses laravel-html-meta Protection

## Summary
Severity: Medium
Advisory: CVE-2026-35516
Aliases: GHSA-4jhm-r4f5-p7xm
CVSS: 5.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-35516
Type: osv

## Details
LinkAce is a self-hosted archive to collect website links. Prior to 2.5.4, LinkRepository::update and CheckLinksCommand::checkLink do not check for private IPs. An authenticated user can read responses from internal services (AWS IMDSv1, cloud metadata, internal APIs) by creating a link with a public URL and then updating it to a private IP. The links:check cron job makes the request server-side without IP filtering. This can expose cloud credentials, internal service data, and network topology. This vulnerability is fixed in 2.5.4.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35516.json
- https://github.com/Kovah/LinkAce/security/advisories/GHSA-4jhm-r4f5-p7xm
- https://nvd.nist.gov/vuln/detail/CVE-2026-35516
