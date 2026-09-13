# [M] ION-DTN < 4.2.1-a.1 Denial of Service via canonicalizePayloadBlock() Assertion

## Summary
Severity: Medium
Advisory: CVE-2026-75584
Aliases: GHSA-9vgc-2r6g-6qwf
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-75584
Type: osv

## Details
ION-DTN before 4.2.1-a.1 contains a denial of service vulnerability that allows unauthenticated remote attackers to crash the ION process by sending a BPv7 bundle with a zero-length payload. The canonicalizePayloadBlock() function in bpsec_util.c passes bundle->payload.length to zco_clone() without validating it against zero, causing a failed CHKZERO assertion that triggers sm_Abort() and terminates the process with SIGABRT before any HMAC verification occurs, requiring no valid key or credential to exploit.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75584.json
- https://github.com/nasa-jpl/ION-DTN/security/advisories/GHSA-9vgc-2r6g-6qwf
- https://nvd.nist.gov/vuln/detail/CVE-2026-75584
- https://www.vulncheck.com/advisories/ion-dtn-a-1-denial-of-service-via-canonicalizepayloadblock-assertion
- https://github.com/nasa-jpl/ION-DTN
