# [H] libcurl might in some circumstances reuse the wrong connection for SMB(S) transfers. libcurl...

## Summary
Severity: High
Advisory: JLSEC-2026-1205
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/JLSEC-2026-1205
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=0 <8.20.0+0
- Julia: `LibCURL_jll` — affected >=0 <8.20.0+0

## Details
libcurl might in some circumstances reuse the wrong connection for SMB(S)
transfers.

libcurl features a pool of recent connections so that subsequent requests can
reuse an existing connection to avoid overhead.

When reusing a connection a range of criteria must be met. Due to a logical
error in the code, a network transfer operation that was requested by an
application could wrongfully reuse an existing SMB connection to the same
server that was using a different 'share' than the new subsequent transfer
should.

This could in unlucky situations lead to the download of the wrong file or the
upload of a file to the wrong place. When this happens, the same credentials
are used and the server name is the same.

## References
- http://www.openwall.com/lists/oss-security/2026/04/29/9
- https://curl.se/docs/CVE-2026-5773.html
- https://curl.se/docs/CVE-2026-5773.json
- https://github.com/advisories/GHSA-rp9q-8q5w-ch44
- https://hackerone.com/reports/3650689
- https://nvd.nist.gov/vuln/detail/CVE-2026-5773
