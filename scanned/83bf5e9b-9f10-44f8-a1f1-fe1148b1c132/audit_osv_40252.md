# [C] Ghidra < 12.1 - Remote Code Execution via Unfiltered RMI Deserialization in Shared Project Connection

## Summary
Severity: Critical
Advisory: CVE-2026-52751
Aliases: GHSA-fgg5-g275-7742
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-52751
Type: osv

## Details
Ghidra before 12.1 contains an unsafe deserialization vulnerability in client-side Shared-Project RMI connection code that allows unauthenticated remote code execution. Attackers can craft a malicious project file with a ghidra:// URL that, when opened via File → Open Project, deserializes untrusted objects using a Jython 2.7.4 gadget chain to execute arbitrary commands.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52751.json
- https://github.com/NationalSecurityAgency/ghidra/security/advisories/GHSA-fgg5-g275-7742
- https://nvd.nist.gov/vuln/detail/CVE-2026-52751
- https://www.vulncheck.com/advisories/ghidra-remote-code-execution-via-unfiltered-rmi-deserialization-in-shared-project-connection
- https://github.com/NationalSecurityAgency/ghidra/commit/91a269103fe5d133c14ec3afa60280dccb94be5c
- https://github.com/nationalsecurityagency/ghidra
