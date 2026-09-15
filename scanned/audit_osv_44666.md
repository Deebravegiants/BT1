# [C] MOOS-IvP through 24.8.1 Out-of-Bounds Write via Unvalidated IvP Payload Counts

## Summary
Severity: Critical
Advisory: CVE-2026-85438
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85438
Type: osv

## Details
MOOS-IvP through 24.8.1 contains a buffer overflow vulnerability in StringToIvPFunction() where dimension, piece, and degree counts from encoded BHV_IPF payloads are used as allocation sizes and loop bounds without validation. Attackers can supply crafted payloads with mismatched dimension values to write attacker-controlled doubles past the end of the IvPBox weight array, causing memory corruption and potential code execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85438.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85438
- https://www.vulncheck.com/advisories/moos-ivp-through-24.8.1-out-of-bounds-write-via-unvalidated-ivp-payload-counts
- https://github.com/moos-ivp/moos-ivp/commit/85f4653ff792b30c3ab14dc0eac0991d1405d904
- https://github.com/moos-ivp/moos-ivp/pull/126
- https://github.com/moos-ivp/moos-ivp
- https://github.com/moos-ivp/moos-ivp/blob/1de9ae146cd63c209e8c3fd81611a4ed2472971b/ivp/src/lib_ivpbuild/FunctionEncoder.cpp#L407
