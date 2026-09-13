# [H] net/rds: No shortcut out of RDS_CONN_ERROR

## Summary
Severity: High
Advisory: CVE-2026-43226
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43226
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <5.10.252, >=5.11.0 <5.15.202, >=5.16.0 <6.1.165, >=6.2.0 <6.6.128, >=6.7.0 <6.12.75, >=6.13.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/rds: No shortcut out of RDS_CONN_ERROR

RDS connections carry a state "rds_conn_path::cp_state"
and transitions from one state to another and are conditional
upon an expected state: "rds_conn_path_transition."

There is one exception to this conditionality, which is
"RDS_CONN_ERROR" that can be enforced by "rds_conn_path_drop"
regardless of what state the condition is currently in.

But as soon as a connection enters state "RDS_CONN_ERROR",
the connection handling code expects it to go through the
shutdown-path.

The RDS/TCP multipath changes added a shortcut out of
"RDS_CONN_ERROR" straight back to "RDS_CONN_CONNECTING"
via "rds_tcp_accept_one_path" (e.g. after "rds_tcp_state_change").

A subsequent "rds_tcp_reset_callbacks" can then transition
the state to "RDS_CONN_RESETTING" with a shutdown-worker queued.

That'll trip up "rds_conn_init_shutdown", which was
never adjusted to handle "RDS_CONN_RESETTING" and subsequently
drops the connection with the dreaded "DR_INV_CONN_STATE",
which leaves "RDS_SHUTDOWN_WORK_QUEUED" on forever.

So we do two things here:

a) Don't shortcut "RDS_CONN_ERROR", but take the longer
   path through the shutdown code.

b) Add "RDS_CONN_RESETTING" to the expected states in
  "rds_conn_init_shutdown" so that we won't error out
  and get stuck, if we ever hit weird state transitions
  like this again."

## References
- https://git.kernel.org/stable/c/19e384a7d00d888303a8285977cdf1970c6cccd6
- https://git.kernel.org/stable/c/81248b1eb3c5954cc1fc7b33b7c03e34d20cb8c8
- https://git.kernel.org/stable/c/899ef00963ce76f9fc421a7d02335fe4ead6389b
- https://git.kernel.org/stable/c/9bcd7c00691a2db9745817d5ea79262a503b135c
- https://git.kernel.org/stable/c/9ff599a9be784a808c36765086e3db2144aa3b66
- https://git.kernel.org/stable/c/a179ac7be8f5a650d0068040705f4cddd6ca369c
- https://git.kernel.org/stable/c/ad22d24be635c6beab6a1fdd3f8b1f3c478d15da
- https://git.kernel.org/stable/c/f0f729bdffb08af32e0f54521b81b8a9e0321f16
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43226.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43226
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
