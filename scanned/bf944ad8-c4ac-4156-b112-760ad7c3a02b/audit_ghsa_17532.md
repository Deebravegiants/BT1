# [H] DNN.PLATFORM leaks NTLM hash via SMB Share Interaction with malicious user input

## Summary
Severity: High
Advisory: GHSA-mgfv-2362-jq96
CVE: CVE-2025-52488
CWE: CWE-200
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2025-06-20
Source: https://github.com/advisories/GHSA-mgfv-2362-jq96
Type: github-advisory

## Affected
- NuGet: `DNN.PLATFORM` — affected >=6.0.0 <10.0.1

## Details
DNN.PLATFORM allows a specially crafted series of malicious interaction can expose NTLM hashes to a third party SMB server. This vulnerability is fixed in 10.0.1.

## References
- https://github.com/dnnsoftware/Dnn.Platform/security/advisories/GHSA-mgfv-2362-jq96
- https://nvd.nist.gov/vuln/detail/CVE-2025-52488
- https://github.com/dnnsoftware/Dnn.Platform
