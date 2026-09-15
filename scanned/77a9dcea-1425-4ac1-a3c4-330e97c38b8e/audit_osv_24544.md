# [C] CVE-2023-22671

## Summary
Severity: Critical
Advisory: CVE-2023-22671
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-06
Source: https://osv.dev/vulnerability/CVE-2023-22671
Type: osv

## Details
Ghidra/RuntimeScripts/Linux/support/launch.sh in NSA Ghidra through 10.2.2 passes user-provided input into eval, leading to command injection when calling analyzeHeadless with untrusted input.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/22xxx/CVE-2023-22671.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-22671
- https://github.com/NationalSecurityAgency/ghidra/issues/4869
- https://github.com/NationalSecurityAgency/ghidra/pull/4872
