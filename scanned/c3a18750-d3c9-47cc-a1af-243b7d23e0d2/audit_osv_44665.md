# [C] MOOS-IvP through 24.8.1 Buffer Overflow in IvP Function String Decoders

## Summary
Severity: Critical
Advisory: CVE-2026-85437
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85437
Type: osv

## Details
MOOS-IvP through 24.8.1 contains multiple buffer overflow vulnerabilities in IvP function string decoders that trust attacker-controlled length fields without validation. Attackers can craft malicious encoded strings with mismatched declared and actual field lengths to overflow heap and stack buffers, potentially achieving remote code execution through MOOS variables or alog files.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85437.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85437
- https://www.vulncheck.com/advisories/moos-ivp-through-24.8.1-buffer-overflow-in-ivp-function-string-decoders
- https://github.com/moos-ivp/moos-ivp/commit/81ca795fcfd62b42002d277f5a2390f4c8ab8c7f
- https://github.com/moos-ivp/moos-ivp/pull/125
- https://github.com/moos-ivp/moos-ivp
- https://github.com/moos-ivp/moos-ivp/blob/1de9ae146cd63c209e8c3fd81611a4ed2472971b/ivp/src/lib_ivpbuild/FunctionEncoder.cpp#L310
