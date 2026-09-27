# [M] FreeRDP before 3.29.0 NULL Dereference via smartcard cleanup

## Summary
Severity: Medium
Advisory: CVE-2026-67304
Aliases: GHSA-78jj-45vh-jpm5
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-01
Source: https://osv.dev/vulnerability/CVE-2026-67304
Type: osv

## Details
FreeRDP before 3.29.0 contains a null pointer dereference vulnerability in smartcard device control request cleanup when reader-state decoding fails. Attackers can send malformed smartcard IRP requests with non-zero cReaders and truncated reader-state data to crash the process via null pointer access in free_reader_states functions.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67304.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-78jj-45vh-jpm5
- https://nvd.nist.gov/vuln/detail/CVE-2026-67304
- https://www.vulncheck.com/advisories/freerdp-before-null-dereference-via-smartcard-cleanup
- https://github.com/FreeRDP/FreeRDP/commit/1cc783d4c78bd2f66d3a8582dfe70a663d141444
