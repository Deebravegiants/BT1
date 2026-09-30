# [C] CVE-2023-25076

## Summary
Severity: Critical
Advisory: CVE-2023-25076
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-03-30
Source: https://osv.dev/vulnerability/CVE-2023-25076
Type: osv

## Details
A buffer overflow vulnerability exists in the handling of wildcard backend hosts of SNIProxy 0.6.0-2 and the master branch (commit: 822bb80df9b7b345cc9eba55df74a07b498819ba). A specially crafted HTTP or TLS packet can lead to arbitrary code execution. An attacker could send a malicious packet to trigger this vulnerability.

## References
- https://lists.debian.org/debian-lts-announce/2023/04/msg00030.html
- https://talosintelligence.com/vulnerability_reports/TALOS-2023-1731
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2023-1731
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/25xxx/CVE-2023-25076.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-25076
- https://www.debian.org/security/2023/dsa-5413
- https://github.com/dlundquist/sniproxy/commit/f8d9a433fe22ab2fa15c00179048ab02ae23d583
