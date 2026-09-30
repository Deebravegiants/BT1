# [M] MyBB: IPv6 SSRF

## Summary
Severity: Medium
Advisory: CVE-2026-45123
Aliases: GHSA-56wr-64wx-5g7j
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-45123
Type: osv

## Details
MyBB is free and open source forum software. Prior to 1.8.40, the remote requests feature does not correctly handle IPv6 addresses, resulting in a server-side request forgery vulnerability. The default disallowed remote hosts list does not include IPv6 addresses. Verification in fetch_remote_file() fails open when get_ip_by_hostname() returns no result because that function does not return IPv6 results, allowing a crafted remote target to bypass the host restriction. The uniquely identifying implementation details include fail-open verification, and inc/functions.php. This issue is fixed in version 1.8.40.

## References
- https://github.com/mybb/mybb/releases/tag/mybb_1840
- https://mybb.com/versions/1.8.40
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45123.json
- https://github.com/mybb/mybb/security/advisories/GHSA-56wr-64wx-5g7j
- https://nvd.nist.gov/vuln/detail/CVE-2026-45123
- https://github.com/mybb/mybb/commit/9cdadbf66f4cef50019f13aaa8e3470ea6535cb7
