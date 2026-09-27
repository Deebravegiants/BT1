# [M] dhcpcd Heap Use-After-Free via Control Socket Handling

## Summary
Severity: Medium
Advisory: CVE-2026-56117
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-23
Source: https://osv.dev/vulnerability/CVE-2026-56117
Type: osv

## Details
dhcpcd through 10.3.2, fixed in commit 78ea09e, contains a heap use-after-free vulnerability in the control socket handling within src/control.c that allows local unprivileged attackers to trigger memory corruption when privilege separation is disabled. Attackers can connect to the control socket and send a privileged command such as -x, causing control_recvdata() to free the client object while the same READ+HANGUP event subsequently reaches control_hangup() with the stale pointer, resulting in a use-after-free condition exploitable in deployments using --disable-privsep or where privsep initialization has failed with the control socket operating in mode 0666.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56117.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-56117
- https://www.vulncheck.com/advisories/dhcpcd-heap-use-after-free-via-control-socket-handling
- https://github.com/NetworkConfiguration/dhcpcd/commit/78ea09ed1633a583dbcde6e7bab9df4639ec8a34
- https://github.com/NetworkConfiguration/dhcpcd
