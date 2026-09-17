# [M] ION-DTN before 4.2.0 Out-of-Bounds Read via decodeSdnv

## Summary
Severity: Medium
Advisory: CVE-2026-84484
Aliases: GHSA-85pw-28vw-2jf7
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-02
Source: https://osv.dev/vulnerability/CVE-2026-84484
Type: osv

## Details
ION-DTN versions before 4.2.0 contain an out-of-bounds read vulnerability in the decodeSdnv function that allows unauthenticated remote attackers to read memory by sending truncated SDNV values. Attackers can send a UDP datagram to the LTP link service input port with a truncated SDNV to trigger reads up to nine bytes past buffer boundaries and underflow byte counters.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84484.json
- https://github.com/nasa-jpl/ION-DTN/releases/tag/ion-open-source-4.2.0
- https://github.com/nasa-jpl/ION-DTN/security/advisories/GHSA-85pw-28vw-2jf7
- https://nvd.nist.gov/vuln/detail/CVE-2026-84484
- https://www.vulncheck.com/advisories/ion-dtn-before-4.2.0-out-of-bounds-read-via-decodesdnv
- https://github.com/nasa-jpl/ION-DTN/commit/d52d22bdd383798712357f86a2778757f740e812
- https://github.com/nasa-jpl/ION-DTN
- https://github.com/nasa-jpl/ION-DTN/blob/ion-open-source-4.1.4/ici/library/ion.c#L1693
- https://github.com/nasa-jpl/ION-DTN/blob/ion-open-source-4.1.4/ici/library/platform.c#L1982
