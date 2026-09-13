# [H] WebSocket endless loop

## Summary
Severity: High
Advisory: CVE-2025-5399
Aliases: CURL-CVE-2025-5399
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-06-07
Source: https://osv.dev/vulnerability/CVE-2025-5399
Type: osv

## Details
Due to a mistake in libcurl's WebSocket code, a malicious server can send a
particularly crafted packet which makes libcurl get trapped in an endless
busy-loop.

There is no other way for the application to escape or exit this loop other
than killing the thread/process.

This might be used to DoS libcurl-using application.

## References
- http://www.openwall.com/lists/oss-security/2025/06/04/2
- https://curl.se/docs/CVE-2025-5399.html
- https://curl.se/docs/CVE-2025-5399.json
- https://hackerone.com/reports/3168039
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/5xxx/CVE-2025-5399.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-5399
