# [C] Stack-Buffer Overflow in 'Content-Length' and 'Warning' Header Processing in sngrep

## Summary
Severity: Critical
Advisory: CVE-2024-3120
CVSS: 9.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-04-09
Source: https://osv.dev/vulnerability/CVE-2024-3120
Type: osv

## Details
A stack-buffer overflow vulnerability exists in all versions of sngrep since v1.4.1. The flaw is due to inadequate bounds checking when copying 'Content-Length' and 'Warning' headers into fixed-size buffers in the sip_validate_packet and sip_parse_extra_headers functions within src/sip.c. This vulnerability allows remote attackers to execute arbitrary code or cause a denial of service (DoS) via crafted SIP messages.

## References
- https://github.com/irontec/sngrep/pull/480/commits/f229a5d31b0be6a6cc3ab4cd9bfa4a1b5c5714c6
- https://github.com/irontec/sngrep/releases/tag/v1.8.1
- https://pentraze.com/vulnerability-reports/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/3xxx/CVE-2024-3120.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-3120
