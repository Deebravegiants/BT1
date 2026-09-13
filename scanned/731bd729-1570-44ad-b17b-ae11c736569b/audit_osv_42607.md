# [M] FreeRDP before 3.30.0 Heap Overflow via CliprdrStream_Read

## Summary
Severity: Medium
Advisory: CVE-2026-68579
Aliases: CVE-2026-76840, GHSA-m37j-jcr2-8gcc
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-02
Source: https://osv.dev/vulnerability/CVE-2026-68579
Type: osv

## Details
FreeRDP before 3.30.0 (<= 3.29.0) contains a heap-based buffer overflow in the Windows clipboard client's CliprdrStream_Read function (client/Windows/wf_cliprdr.c). When an OLE paste consumer (e.g. explorer.exe) calls IStream::Read with a fixed-size buffer of cb bytes, CliprdrStream_Read requests file contents from the RDP server and then copies the response into the caller's buffer using the server-supplied length (req_fsize) instead of cb. A malicious or compromised RDP server can return an oversized CB_FILECONTENTS_RESPONSE, causing an out-of-bounds write of attacker-controlled data into the paste consumer's heap buffer when a user pastes server-offered clipboard file contents.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68579.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-m37j-jcr2-8gcc
- https://nvd.nist.gov/vuln/detail/CVE-2026-68579
- https://www.vulncheck.com/advisories/freerdp-before-heap-overflow-via-cliprdrstream-read
- https://github.com/FreeRDP/FreeRDP/commit/5e8e987b469b60a3bafadf8f5afc40f91c09f458
