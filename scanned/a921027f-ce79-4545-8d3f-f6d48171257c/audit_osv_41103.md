# [H] wrong reuse of SMB connection

## Summary
Severity: High
Advisory: CVE-2026-5773
Aliases: CURL-CVE-2026-5773
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-05-13
Source: https://osv.dev/vulnerability/CVE-2026-5773
Type: osv

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
- https://hackerone.com/reports/3650689
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/5xxx/CVE-2026-5773.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-5773
