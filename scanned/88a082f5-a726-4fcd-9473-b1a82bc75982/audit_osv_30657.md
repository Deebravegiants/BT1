# [M] Improper Initialization of `imc` Scheme Leading to `SIGABRT` in ION-DTN BPv7

## Summary
Severity: Medium
Advisory: CVE-2024-54129
Aliases: GHSA-393w-w6jh-pq3j
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H)
Published: 2024-12-05
Source: https://osv.dev/vulnerability/CVE-2024-54129
Type: osv

## Details
The NASA’s Interplanetary Overlay Network (ION) is an implementation of Delay/Disruption Tolerant Networking (DTN). A vulnerability exists in the version ION-DTN BPv7 implementation version 4.1.3 when receiving a bundle with an improper reference to the imc scheme with valid Service-Specific Part (SSP) in their Previous Node Block. The vulnerability can cause ION to become unresponsive. This vulnerability is fixed in 4.1.3s.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/54xxx/CVE-2024-54129.json
- https://github.com/nasa-jpl/ION-DTN/security/advisories/GHSA-393w-w6jh-pq3j
- https://nvd.nist.gov/vuln/detail/CVE-2024-54129
