# [M] ALPINE-CVE-2026-62436

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-62436
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2026-07-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-62436
Type: osv

## Affected
- Alpine:v3.21: `xen` — affected >=0 <4.19.6-r0
- Alpine:v3.22: `xen` — affected >=0 <4.20.4-r0
- Alpine:v3.23: `xen` — affected >=0 <4.20.4-r0
- Alpine:v3.24: `xen` — affected >=0 <4.21.2-r0

## Details
[This CNA information record relates to multiple CVEs; the
text explains which aspects/vulnerabilities correspond to which CVE.]

With the introduction of Grant Table v2 came the requirement to be able to
switch between versions.  Switching from v1 to v2 reduces the number of
valid grant references, as a bigger shared entry structure is then needed
while the shared table doesn't change size.  Switching from v2 back to v1
the status frames, which are separate in v2, go away.

Code holding, but intermediately dropping and then re-acquiring the grant
table lock, sometimes wrongly assumes that said properties wouldn't change
across the window in time where the lock is not being held.

The v1 -> v2 issue is CVE-2026-62435.

The v2 -> v1 issue is CVE-2026-62436.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-62436
