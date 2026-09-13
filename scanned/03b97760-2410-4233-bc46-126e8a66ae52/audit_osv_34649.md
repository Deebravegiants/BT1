# [M] CVE-2025-63384

## Summary
Severity: Medium
Advisory: CVE-2025-63384
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-11-10
Source: https://osv.dev/vulnerability/CVE-2025-63384
Type: osv

## Details
A vulnerability was discovered in RISC-V Rocket-Chip v1.6 and before implementation where the SRET (Supervisor-mode Exception Return) instruction fails to correctly transition the processor's privilege level. Instead of downgrading from Machine-mode (M-mode) to Supervisor-mode (S-mode) as specified by the sstatus.SPP bit, the processor incorrectly remains in M-mode, leading to a critical privilege retention vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/63xxx/CVE-2025-63384.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-63384
- https://github.com/107040503/RISC-V-Vulnerability-Disclosure_SRET
- https://github.com/chipsalliance/rocket-chip.git
