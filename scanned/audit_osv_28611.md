# [H] CVE-2024-35434

## Summary
Severity: High
Advisory: CVE-2024-35434
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-29
Source: https://osv.dev/vulnerability/CVE-2024-35434
Type: osv

## Details
Irontec Sngrep v1.8.1 was discovered to contain a heap buffer overflow via the function rtp_check_packet at /sngrep/src/rtp.c. This vulnerability allows attackers to cause a Denial of Service (DoS) via a crafted SIP packet.

## References
- https://github.com/inputzero/Security-Advisories/blob/main/CVE-XXXX-XXXX.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35434.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35434
