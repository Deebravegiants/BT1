# [H] Unbounded Memory Allocation in Stalwart IMAP parser

## Summary
Severity: High
Advisory: CVE-2025-61600
Aliases: GHSA-8jqj-qj5p-v5rr
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-02
Source: https://osv.dev/vulnerability/CVE-2025-61600
Type: osv

## Details
Stalwart is a mail and collaboration server. Versions 0.13.3 and below contain an unbounded memory allocation vulnerability in the IMAP protocol parser which allows remote attackers to exhaust server memory, potentially triggering the system's out-of-memory (OOM) killer and causing a denial of service. The CommandParser implementation enforces size limits on its dynamic buffer in most parsing states, but several state handlers omit these validation checks. This issue is fixed in version 0.13.4. A workaround for this issue is to implement rate limiting and connection monitoring at the network level, however this does not provide complete protection.

## References
- https://github.com/stalwartlabs/stalwart/releases/tag/v0.13.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/61xxx/CVE-2025-61600.json
- https://github.com/stalwartlabs/stalwart/security/advisories/GHSA-8jqj-qj5p-v5rr
- https://nvd.nist.gov/vuln/detail/CVE-2025-61600
- https://github.com/stalwartlabs/stalwart/commit/a8e631e881bded8128358732f18e02ca94a4e677
