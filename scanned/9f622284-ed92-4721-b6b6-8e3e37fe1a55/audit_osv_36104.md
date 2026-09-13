# [M] Deciso OPNsense diag_backup.php filename Command Injection Remote Code Execution Vulnerability

## Summary
Severity: Medium
Advisory: CVE-2026-2035
CVSS: 6.8 (CVSS:3.0/AV:A/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-20
Source: https://osv.dev/vulnerability/CVE-2026-2035
Type: osv

## Details
Deciso OPNsense diag_backup.php filename Command Injection Remote Code Execution Vulnerability. This vulnerability allows network-adjacent attackers to execute arbitrary code on affected installations of Deciso OPNsense. Authentication is required to exploit this vulnerability.

The specific flaw exists within the handling of backup configuration files. The issue results from the lack of proper validation of a user-supplied string before using it to execute a system call. An attacker can leverage this vulnerability to execute code in the context of root. Was ZDI-CAN-28131.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/2xxx/CVE-2026-2035.json
- https://github.com/opnsense/core/commit/cb15c935137d05c86a1e6cf12af877e9c32a23af
- https://nvd.nist.gov/vuln/detail/CVE-2026-2035
- https://www.zerodayinitiative.com/advisories/ZDI-26-078/
