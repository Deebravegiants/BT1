# [M] Reachable Assertion vulnerability in Open5GS

## Summary
Severity: Medium
Advisory: CVE-2025-41067
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:L)
Published: 2025-10-27
Source: https://osv.dev/vulnerability/CVE-2025-41067
Type: osv

## Details
Reachable Assertion vulnerability in Open5GS up to version 2.7.6 allows attackers with connectivity to the NRF to cause a denial of service. An SBI request that deletes the NRF's own registry causes a check that ends up crashing the NRF process and renders the discovery service unavailable.

## References
- https://www.incibe.es/en/incibe-cert/notices/aviso/multiple-vulnerabilities-newplanes-open5gs
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/41xxx/CVE-2025-41067.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-41067
- https://open5gs.org/open5gs/release/2025/07/19/release-v2.7.6.html
