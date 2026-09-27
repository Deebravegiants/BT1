# [H] CVE-2024-36844

## Summary
Severity: High
Advisory: CVE-2024-36844
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-31
Source: https://osv.dev/vulnerability/CVE-2024-36844
Type: osv

## Details
libmodbus v3.1.6 was discovered to contain a use-after-free via the ctx->backend pointer. This vulnerability allows attackers to cause a Denial of Service (DoS) via a crafted message sent to the unit-test-server.

## References
- https://lists.debian.org/debian-lts-announce/2025/03/msg00010.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36844.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36844
- https://github.com/stephane/libmodbus/issues/749
