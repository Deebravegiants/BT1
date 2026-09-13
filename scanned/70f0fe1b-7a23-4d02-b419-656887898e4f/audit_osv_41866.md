# [C] ksmbd: fix durable reconnect error path file lifetime

## Summary
Severity: Critical
Advisory: CVE-2026-64016
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64016
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.33 <6.18.34, >=7.0.10 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix durable reconnect error path file lifetime

After a durable reconnect succeeds, ksmbd_reopen_durable_fd() republishes
the same ksmbd_file into the session volatile-id table. If smb2_open()
then takes a later error path, cleanup first calls ksmbd_fd_put(work, fp)
and then unconditionally calls ksmbd_put_durable_fd(dh_info.fp).

In this case fp and dh_info.fp are the same object. The first put drops the
reconnect lookup reference, but the final durable put can run
__ksmbd_close_fd(NULL, fp). Because the final close is not session-aware,
it can free the file object without removing the volatile-id entry that was
just published into the session table.

Use the session-aware put for the final reconnect drop when the reconnect
had already succeeded and the error path is cleaning up the republished
file. Earlier reconnect failures, before fp is assigned to dh_info.fp, keep
using the durable-only put path.

## References
- https://git.kernel.org/stable/c/3515503322f4819277091839eed46b695096aca5
- https://git.kernel.org/stable/c/6cb0b9385320110fe24a5d5ac0000ade4bb3a3f3
- https://git.kernel.org/stable/c/a1a39f227c80cbf369767badc32cba2b225147d1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64016.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64016
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
