# [H] When a libcurl-based application performs transfers via `SCP://` or `SFTP://` and utilizes the ...

## Summary
Severity: High
Advisory: JLSEC-2026-1222
Ecosystem: Julia
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/JLSEC-2026-1222
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=0 <8.21.0+0
- Julia: `LibCURL_jll` — affected >=7.70.0+0 <8.21.0+0

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
- https://github.com/advisories/GHSA-xq9p-gxg6-f7q6
- https://hackerone.com/reports/3751712
- https://nvd.nist.gov/vuln/detail/CVE-2026-9547
