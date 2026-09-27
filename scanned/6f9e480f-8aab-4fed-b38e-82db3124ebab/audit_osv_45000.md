# [H] SSH improper host validation

## Summary
Severity: High
Advisory: CVE-2026-9547
Aliases: CURL-CVE-2026-9547
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-07-03
Source: https://osv.dev/vulnerability/CVE-2026-9547
Type: osv

## Details
When a libcurl-based application performs transfers via `SCP://` or `SFTP://`
and utilizes the `CURLOPT_SSH_KEYFUNCTION` callback, it may silently accept an
untrusted server. This vulnerability occurs when a server presents a host key
type that does not match the specific key type already recorded for that host
in the `known_hosts` file. Instead of rejecting the mismatch, the callback
mechanism fails to properly enforce the restriction, allowing the connection
to succeed without warning and risking a potential man-in-the-middle attack.

## References
- https://curl.se/docs/CVE-2026-9547.html
- https://curl.se/docs/CVE-2026-9547.json
- https://hackerone.com/reports/3751712
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/9xxx/CVE-2026-9547.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-9547
