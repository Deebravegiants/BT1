# [H] When a user invokes curl using a schemeless URL combined with `--proto-default` sftp (or scp), a...

## Summary
Severity: High
Advisory: JLSEC-2026-1202
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/JLSEC-2026-1202
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=0 <8.21.0+0
- Julia: `LibCURL_jll` — affected >=7.81.0+0 <8.21.0+0

## Details
When a user invokes curl using a schemeless URL combined with
`--proto-default` sftp (or scp), a disconnect occurs between the tool layer
and libcurl. The tool layer incorrectly infers the URL scheme, which
erroneously bypasses the initialization of critical SSH security options like
`CURLOPT_SSH_HOST_PUBLIC_KEY_SHA256` and `CURLOPT_SSH_KNOWNHOSTS`. Conversely, the
libcurl runtime successfully honors `CURLOPT_DEFAULT_PROTOCOL` and establishes
the connection via SFTP/SCP as specified. Because the tool layer skipped the
security configuration, these SSH host verification options are silently
omitted, causing curl to connect to an unverified SSH remote host without
throwing an error.

## References
- https://curl.se/docs/CVE-2026-12064.html
- https://curl.se/docs/CVE-2026-12064.json
- https://github.com/advisories/GHSA-jm94-9f7h-36pr
- https://hackerone.com/reports/3797526
- https://nvd.nist.gov/vuln/detail/CVE-2026-12064
