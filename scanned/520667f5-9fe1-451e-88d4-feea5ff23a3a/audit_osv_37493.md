# [H] smb: server: fix active_num_conn leak on transport allocation failure

## Summary
Severity: High
Advisory: CVE-2026-31711
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-31711
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.210, >=5.16.0 <6.1.175, >=6.2.0 <6.12.84, >=6.7.0 <6.18.25, >=6.13.0 <7.0.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: server: fix active_num_conn leak on transport allocation failure

Commit 77ffbcac4e56 ("smb: server: fix leak of active_num_conn in
ksmbd_tcp_new_connection()") addressed the kthread_run() failure
path.  The earlier alloc_transport() == NULL path in the same
function has the same leak, is reachable pre-authentication via any
TCP connect to port 445, and was empirically reproduced on UML
(ARCH=um, v7.0-rc7): a small number of forced allocation failures
were sufficient to put ksmbd into a state where every subsequent
connection attempt was rejected for the remainder of the boot.

ksmbd_kthread_fn() increments active_num_conn before calling
ksmbd_tcp_new_connection() and discards the return value, so when
alloc_transport() returns NULL the socket is released and -ENOMEM
returned without decrementing the counter.  Each such failure
permanently consumes one slot from the max_connections pool; once
cumulative failures reach the cap, atomic_inc_return() hits the
threshold on every subsequent accept and every new connection is
rejected.  The counter is only reset by module reload.

An unauthenticated remote attacker can drive the server toward the
memory pressure that makes alloc_transport() fail by holding open
connections with large RFC1002 lengths up to MAX_STREAM_PROT_LEN
(0x00FFFFFF); natural transient allocation failures on a loaded
host produce the same drift more slowly.

Mirror the existing rollback pattern in ksmbd_kthread_fn(): on the
alloc_transport() failure path, decrement active_num_conn gated on
server_conf.max_connections.

Repro details: with the patch reverted, forced alloc_transport()
NULL returns leaked counter slots and subsequent connection
attempts -- including legitimate connects issued after the
forced-fail window had closed -- were all rejected with "Limit the
maximum number of connections".  With this patch applied, the same
connect sequence produces no rejections and the counter cycles
cleanly between zero and one on every accept.

## References
- https://git.kernel.org/stable/c/283027aa93380380a0994f35dde3ec95318f2654
- https://git.kernel.org/stable/c/295a9fc6789d1011c36ded9f0f2907bb34fa0de4
- https://git.kernel.org/stable/c/60734c8bc3b4aa0672e251f08dda81977e4b5387
- https://git.kernel.org/stable/c/6551300dc452ac16a855a83dbd1e74899542d3b3
- https://git.kernel.org/stable/c/97f8d2648ef4871e4cd335e2d769cb40054a6772
- https://git.kernel.org/stable/c/dc2e7d595d68cf1be1ba64e3d30ebf3266bf7242
- https://git.kernel.org/stable/c/fb48185bcd946d42de7017cf27f912f8ab26acf0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31711.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31711
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
