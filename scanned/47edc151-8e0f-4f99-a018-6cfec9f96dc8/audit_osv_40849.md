# [M] GoAccess WebSocket Server: Signed 32 bit truncation of the 64 bit frame length causes a remote pre-authentication denial of service

## Summary
Severity: Medium
Advisory: CVE-2026-55768
Aliases: GHSA-5gm5-pvh2-wg46
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/CVE-2026-55768
Type: osv

## Details
GoAccess is a real-time web log analyzer and interactive viewer that runs in a terminal in *nix systems or through the browser. Prior to version 1.11, the built-in WebSocket server narrows a 64-bit extended frame length into the signed 32-bit WSFrame.payloadlen field before enforcing the maximum frame size, allowing an unauthenticated remote client to bypass the guard and force an approximately 18-exabyte allocation request that terminates the process. This issue is fixed in version 1.11.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55768.json
- https://github.com/allinurl/goaccess/security/advisories/GHSA-5gm5-pvh2-wg46
- https://nvd.nist.gov/vuln/detail/CVE-2026-55768
- https://github.com/allinurl/goaccess/commit/ea74b87254d0adc675c087ff49bddd2d60dc01d5
