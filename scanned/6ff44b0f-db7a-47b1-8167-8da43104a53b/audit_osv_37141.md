# [M] SWUpdate Integer Underflow in Multipart Upload Parser

## Summary
Severity: Medium
Advisory: CVE-2026-28525
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-23
Source: https://osv.dev/vulnerability/CVE-2026-28525
Type: osv

## Details
SWUpdate contains an integer underflow vulnerability in the multipart upload parser in mongoose_multipart.c that allows unauthenticated attackers to cause a denial of service by sending a crafted HTTP POST request to /upload with a malformed multipart boundary and controlled TCP stream timing. Attackers can trigger an integer underflow in the mg_http_multipart_continue_wait_for_chunk() function when the buffer length falls within a specific range, causing an out-of-bounds heap read past the allocated receive buffer to a local IPC socket.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28525.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-28525
- https://www.vulncheck.com/advisories/swupdate-integer-underflow-in-multipart-upload-parser
- https://github.com/sbabic/swupdate/commit/beee2dc0feef1cfe84f1aa6fc980e104b2e47a74
- https://github.com/sbabic/swupdate
