# [H] CVE-2026-12942

## Summary
Severity: High
Advisory: CVE-2026-12942
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/CVE-2026-12942
Type: osv

## Details
IBM Langflow OSS 1.0.0 through 1.10.1 could allow a remote attacker to traverse directories on the system. An attacker could send a specially crafted URL request containing "dot dot " sequences ( /.. /) to view arbitrary files on the system.

## References
- https://www.ibm.com/support/pages/node/7279993
