# [M] FreeRDP: DoS via WINPR_ASSERT in IMA ADPCM audio decoder (dsp.c:331)

## Summary
Severity: Medium
Advisory: CVE-2026-33977
Aliases: GHSA-8f2g-3q27-6xm5
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-03-30
Source: https://osv.dev/vulnerability/CVE-2026-33977
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to version 3.24.2, a malicious RDP server can crash the FreeRDP client by sending audio data in IMA ADPCM format with an invalid initial step index value (>= 89). The unvalidated step index is read directly from the network and used to index into a 89-entry lookup table, triggering a WINPR_ASSERT() failure and process abort via SIGABRT. This affects any FreeRDP client that has audio redirection (RDPSND) enabled, which is the default configuration. This issue has been patched in version 3.24.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33977.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-8f2g-3q27-6xm5
- https://nvd.nist.gov/vuln/detail/CVE-2026-33977
- https://github.com/FreeRDP/FreeRDP/commit/9be3f03d94a50892fd58a9f7dee72b2313c69b47
