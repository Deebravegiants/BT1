# [M] cpp-httplib vulnerable to a denial of service (DOS) using a zip bomb

## Summary
Severity: Medium
Advisory: CVE-2026-22776
Aliases: GHSA-h934-98h4-j43q
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-01-12
Source: https://osv.dev/vulnerability/CVE-2026-22776
Type: osv

## Details
cpp-httplib is a C++11 single-file header-only cross platform HTTP/HTTPS library. Prior to version 0.30.1, a Denial of Service (DoS) vulnerability exists in cpp-httplib due to the unsafe handling of compressed HTTP request bodies (Content-Encoding: gzip, br, etc.). The library validates the payload_max_length against the compressed data size received from the network, but does not limit the size of the decompressed data stored in memory.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22776.json
- https://github.com/yhirose/cpp-httplib/security/advisories/GHSA-h934-98h4-j43q
- https://nvd.nist.gov/vuln/detail/CVE-2026-22776
- https://github.com/yhirose/cpp-httplib/commit/2e2e47bab1ae6a853476eecbc4bf279dd1fef792
