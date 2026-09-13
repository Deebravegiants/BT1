# [H] mod_gnutls contains Infinite Loop on request read timeout

## Summary
Severity: High
Advisory: CVE-2023-25824
Aliases: GHSA-6cfv-fvgm-7pc8
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-02-23
Source: https://osv.dev/vulnerability/CVE-2023-25824
Type: osv

## Details
Mod_gnutls is a TLS module for Apache HTTPD based on GnuTLS. Versions from 0.9.0 to 0.12.0 (including) did not properly fail blocking read operations on TLS connections when the transport hit timeouts. Instead it entered an endless loop retrying the read operation, consuming CPU resources. This could be exploited for denial of service attacks. If trace level logging was enabled, it would also produce an excessive amount of log output during the loop, consuming disk space. The problem has been fixed in commit d7eec4e598158ab6a98bf505354e84352f9715ec, please update to version 0.12.1. There are no workarounds, users who cannot update should apply the errno fix detailed in the security advisory.

## References
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=942737#25
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/25xxx/CVE-2023-25824.json
- https://github.com/airtower-luna/mod_gnutls/security/advisories/GHSA-6cfv-fvgm-7pc8
- https://nvd.nist.gov/vuln/detail/CVE-2023-25824
- https://github.com/airtower-luna/mod_gnutls/commit/d7eec4e598158ab6a98bf505354e84352f9715ec
