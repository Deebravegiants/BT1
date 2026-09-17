# [M] ALPINE-CVE-2026-56117

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-56117
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-56117
Type: osv

## Affected
- Alpine:v3.23: `dhcpcd` — affected >=0 <10.5.2-r0
- Alpine:v3.24: `dhcpcd` — affected >=0 <10.5.2-r0

## Details
dhcpcd through 10.3.2, fixed in commit 78ea09e, contains a heap use-after-free vulnerability in the control socket handling within src/control.c that allows local unprivileged attackers to trigger memory corruption when privilege separation is disabled. Attackers can connect to the control socket and send a privileged command such as -x, causing control_recvdata() to free the client object while the same READ+HANGUP event subsequently reaches control_hangup() with the stale pointer, resulting in a use-after-free condition exploitable in deployments using --disable-privsep or where privsep initialization has failed with the control socket operating in mode 0666.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-56117
