# [M] CVE-2024-55913

## Summary
Severity: Medium
Advisory: CVE-2024-55913
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-05-02
Source: https://osv.dev/vulnerability/CVE-2024-55913
Type: osv

## Details
IBM Concert Software 1.0.0 through 1.0.5 could allow a remote attacker to traverse directories on the system. An attacker could send a specially crafted URL request containing "dot dot" sequences (/../) to view arbitrary files on the system.

## References
- https://www.ibm.com/support/pages/node/7232169
