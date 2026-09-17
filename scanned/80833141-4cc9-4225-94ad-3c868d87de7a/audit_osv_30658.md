# [M] Segmentation Fault in `forwardBundle` Function of ION-DTN BPv7 When Destination EID is `dtn:none` (public)

## Summary
Severity: Medium
Advisory: CVE-2024-54130
Aliases: GHSA-7pj7-hfwv-q3v6
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H)
Published: 2024-12-05
Source: https://osv.dev/vulnerability/CVE-2024-54130
Type: osv

## Details
The NASA’s Interplanetary Overlay Network (ION) is an implementation of Delay/Disruption Tolerant Networking (DTN). A segmentation fault occurs with ION-DTN BPv7 software version 4.1.3 when a bundle with a Destination Endpoint ID (EID) set to dtn:none is received. This causes the node to become unresponsive to incoming bundles, leading to a Denial of Service (DoS) condition. This vulnerability is fixed in 4.1.3s.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/54xxx/CVE-2024-54130.json
- https://github.com/nasa-jpl/ION-DTN/security/advisories/GHSA-7pj7-hfwv-q3v6
- https://nvd.nist.gov/vuln/detail/CVE-2024-54130
