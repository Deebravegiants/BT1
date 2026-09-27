# [H] proto-default skips SSH verification

## Summary
Severity: High
Advisory: CVE-2026-12064
Aliases: CURL-CVE-2026-12064
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-07-03
Source: https://osv.dev/vulnerability/CVE-2026-12064
Type: osv

## Details
When a user invokes curl using a schemeless URL combined with
`--proto-default` sftp (or scp), a disconnect occurs between the tool layer
and libcurl. The tool layer incorrectly infers the URL scheme, which
erroneously bypasses the initialization of critical SSH security options like
CURLOPT_SSH_HOST_PUBLIC_KEY_SHA256 and CURLOPT_SSH_KNOWNHOSTS. Conversely, the
libcurl runtime successfully honors CURLOPT_DEFAULT_PROTOCOL and establishes
the connection via SFTP/SCP as specified. Because the tool layer skipped the
security configuration, these SSH host verification options are silently
omitted, causing curl to connect to an unverified SSH remote host without
throwing an error.

## References
- https://curl.se/docs/CVE-2026-12064.html
- https://curl.se/docs/CVE-2026-12064.json
- https://hackerone.com/reports/3797526
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/12xxx/CVE-2026-12064.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-12064
