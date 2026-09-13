# [C] AIS-catcher has a Buffer Overflow vulnerability in `AIS::Message` leading to DoS/RCE

## Summary
Severity: Critical
Advisory: CVE-2025-66216
Aliases: GHSA-v53x-f5hh-g2g6
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-11-29
Source: https://osv.dev/vulnerability/CVE-2025-66216
Type: osv

## Details
AIS-catcher is a multi-platform AIS receiver. Prior to version 0.64, a heap buffer overflow vulnerability has been identified in the AIS::Message class of AIS-catcher. This vulnerability allows an attacker to write approximately 1KB of arbitrary data into a 128-byte buffer. This issue has been patched in version 0.64.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66216.json
- https://github.com/jvde-github/AIS-catcher/security/advisories/GHSA-v53x-f5hh-g2g6
- https://nvd.nist.gov/vuln/detail/CVE-2025-66216
- https://github.com/jvde-github/AIS-catcher/commit/3de0ef785fc3c96265a71b37df7b0a82cb279312
