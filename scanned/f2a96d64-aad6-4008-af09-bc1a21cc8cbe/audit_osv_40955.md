# [M] FreeRDP - Use-After-Free via Race Condition in DRDYNVC Channel Callback

## Summary
Severity: Medium
Advisory: CVE-2026-56297
Aliases: GHSA-3mv2-5q57-2v8h
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:L/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/CVE-2026-56297
Type: osv

## Details
FreeRDP before 3.22.0 contains a use-after-free vulnerability in dvcman_channel_close and dvcman_call_on_receive due to improper synchronization of channel_callback access. A malicious RDP server can trigger a race condition by sending DYNVC_DATA and DYNVC_CLOSE messages concurrently, causing heap-use-after-free in the drdynvc client thread and potentially enabling remote code execution or denial of service.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56297.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-3mv2-5q57-2v8h
- https://nvd.nist.gov/vuln/detail/CVE-2026-56297
- https://www.vulncheck.com/advisories/freerdp-use-after-free-via-race-condition-in-drdynvc-channel-callback
