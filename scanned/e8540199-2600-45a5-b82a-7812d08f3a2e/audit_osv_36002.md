# [C] Ghidra Swift Demangler Analyzer Arbitrary Code Execution via Project State

## Summary
Severity: Critical
Advisory: CVE-2026-18718
Aliases: GHSA-pcfh-853f-q3gh
CVSS: 9.0 (CVSS:4.0/AV:L/AC:H/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-18718
Type: osv

## Details
Ghidra contains an arbitrary code execution vulnerability in the Swift demangler analyzer that allows an attacker to execute arbitrary binaries by supplying a malicious Ghidra project with a crafted Swift tool directory path. When a victim opens the attacker-supplied project, SwiftDemanglerAnalyzer restores the persisted Swift binary directory from project state and SwiftNativeDemangler executes the resolved binary without integrity or signature verification, causing attacker-controlled executables to run under the Ghidra process user with no prompt or confirmation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/18xxx/CVE-2026-18718.json
- https://github.com/NationalSecurityAgency/ghidra/security/advisories/GHSA-pcfh-853f-q3gh
- https://nvd.nist.gov/vuln/detail/CVE-2026-18718
- https://www.vulncheck.com/advisories/ghidra-swift-demangler-analyzer-arbitrary-code-execution-via-project-state
- https://github.com/NationalSecurityAgency/ghidra/commit/c03a70d
- https://github.com/NationalSecurityAgency/ghidra
- https://github.com/sn0x-sharma/CVE-2026-18718
- https://sn0xs-organization.gitbook.io/sn0x-order.org/bb-web-hunt/critical/how-i-found-a-0-day-in-ghidra-shared-project-file-became-a-code-execution-vector
