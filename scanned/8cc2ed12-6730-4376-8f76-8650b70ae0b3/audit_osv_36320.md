# [H] net: can: j1939: j1939_xtp_rx_rts_session_active(): deactivate session upon receiving the second rts

## Summary
Severity: High
Advisory: CVE-2026-22997
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-25
Source: https://osv.dev/vulnerability/CVE-2026-22997
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.0 <5.10.249, >=5.11.0 <5.15.199, >=5.16.0 <6.1.162, >=6.2.0 <6.6.122, >=6.7.0 <6.12.67, >=6.13.0 <6.18.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: can: j1939: j1939_xtp_rx_rts_session_active(): deactivate session upon receiving the second rts

Since j1939_session_deactivate_activate_next() in j1939_tp_rxtimer() is
called only when the timer is enabled, we need to call
j1939_session_deactivate_activate_next() if we cancelled the timer.
Otherwise, refcount for j1939_session leaks, which will later appear as

| unregister_netdevice: waiting for vcan0 to become free. Usage count = 2.

problem.

## References
- https://git.kernel.org/stable/c/1809c82aa073a11b7d335ae932d81ce51a588a4a
- https://git.kernel.org/stable/c/6121b7564c725b632ffe4764abe85aa239d37703
- https://git.kernel.org/stable/c/809a437e27a3bf3c1c6c8c157773635552116f2b
- https://git.kernel.org/stable/c/a73e7d7e346dae1c22dc3e95b02ca464b12daf2c
- https://git.kernel.org/stable/c/adabf01c19561e42899da9de56a6a1da0e6b8a5b
- https://git.kernel.org/stable/c/b1d67607e97d489c0cfbbf55f48a76b00710b0e4
- https://git.kernel.org/stable/c/cb2a610867bc379988bae0bb4b8bbc59c0decf1a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22997.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-22997
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
