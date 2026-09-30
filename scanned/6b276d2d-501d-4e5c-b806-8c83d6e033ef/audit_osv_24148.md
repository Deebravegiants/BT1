# [C] scsi: target: iscsi: Fix a race condition between login_work and the login thread

## Summary
Severity: Critical
Advisory: CVE-2022-50350
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2022-50350
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.12.0 <6.0.16, >=6.1.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: target: iscsi: Fix a race condition between login_work and the login thread

In case a malicious initiator sends some random data immediately after a
login PDU; the iscsi_target_sk_data_ready() callback will schedule the
login_work and, at the same time, the negotiation may end without clearing
the LOGIN_FLAGS_INITIAL_PDU flag (because no additional PDU exchanges are
required to complete the login).

The login has been completed but the login_work function will find the
LOGIN_FLAGS_INITIAL_PDU flag set and will never stop from rescheduling
itself; at this point, if the initiator drops the connection, the
iscsit_conn structure will be freed, login_work will dereference a released
socket structure and the kernel crashes.

BUG: kernel NULL pointer dereference, address: 0000000000000230
PF: supervisor write access in kernel mode
PF: error_code(0x0002) - not-present page
Workqueue: events iscsi_target_do_login_rx [iscsi_target_mod]
RIP: 0010:_raw_read_lock_bh+0x15/0x30
Call trace:
 iscsi_target_do_login_rx+0x75/0x3f0 [iscsi_target_mod]
 process_one_work+0x1e8/0x3c0

Fix this bug by forcing login_work to stop after the login has been
completed and the socket callbacks have been restored.

Add a comment to clearify the return values of iscsi_target_do_login()

## References
- https://git.kernel.org/stable/c/1533b8b3058db618409f41554ebe768c2e3acfae
- https://git.kernel.org/stable/c/3ecdca49ca49d4770639d81503c873b6d25887c4
- https://git.kernel.org/stable/c/fec1b2fa62c162d03f5dcd7b03e3c89d3116d49f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50350.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50350
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
