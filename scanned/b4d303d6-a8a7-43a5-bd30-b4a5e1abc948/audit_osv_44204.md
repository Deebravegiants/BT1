# [C] mptcp: fastopen: only mark MPTFO subflows with SYN data

## Summary
Severity: Critical
Advisory: CVE-2026-80585
Ecosystem: Linux
CVSS: 9.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80585
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.153, >=6.7.0 <6.12.105, >=6.13.0 <6.18.46, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

mptcp: fastopen: only mark MPTFO subflows with SYN data

Passive TCP Fast Open accepts a valid-cookie SYN even when it carries
no data. In that case the child socket's receive queue is intentionally
left empty.

mptcp_fastopen_subflow_synack_set_params() set is_mptfo before checking
for queued SYN data. That made data-less TFO SYNs hit a WARN and, if
the warning was non-fatal, left stale MPTFO state behind. The stale
flag could later trigger a state-confusion bug in
check_fully_established().

Only mark the subflow as MPTFO after confirming that an SKB was queued.
Return quietly when the receive queue is empty.

Note that mptcp_subflow_context's is_mptfo field is now not just about
subflows where the TFO was present, but about MPTFO subflow that
consumed SYN data. Only having a valid cookie but not carrying data is
not really "doing TFO".

## References
- https://git.kernel.org/stable/c/72b4a0c51a4b550d40301d60a366b429b8c8e78d
- https://git.kernel.org/stable/c/75e564b2ced1cc3d9a8904c7d2d2bb448fffb8b5
- https://git.kernel.org/stable/c/e00b63056fb4f261455b3e5df5268a1f8ce47a87
- https://git.kernel.org/stable/c/f75f174edc865738522e514d042cf5627f084859
- https://git.kernel.org/stable/c/fca7e444c04689fe4cc6b56f2725f804a4bb1ef9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80585.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80585
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
