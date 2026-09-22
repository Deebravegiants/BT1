# [C] scsi: target: iscsi: Fix timeout on deleted connection

## Summary
Severity: Critical
Advisory: CVE-2025-38075
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2025-38075
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.1.0 <5.4.294, >=5.5.0 <5.10.238, >=5.11.0 <5.15.185, >=5.16.0 <6.1.141, >=6.2.0 <6.6.93, >=6.7.0 <6.12.31, >=6.13.0 <6.14.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: target: iscsi: Fix timeout on deleted connection

NOPIN response timer may expire on a deleted connection and crash with
such logs:

Did not receive response to NOPIN on CID: 0, failing connection for I_T Nexus (null),i,0x00023d000125,iqn.2017-01.com.iscsi.target,t,0x3d

BUG: Kernel NULL pointer dereference on read at 0x00000000
NIP  strlcpy+0x8/0xb0
LR iscsit_fill_cxn_timeout_err_stats+0x5c/0xc0 [iscsi_target_mod]
Call Trace:
 iscsit_handle_nopin_response_timeout+0xfc/0x120 [iscsi_target_mod]
 call_timer_fn+0x58/0x1f0
 run_timer_softirq+0x740/0x860
 __do_softirq+0x16c/0x420
 irq_exit+0x188/0x1c0
 timer_interrupt+0x184/0x410

That is because nopin response timer may be re-started on nopin timer
expiration.

Stop nopin timer before stopping the nopin response timer to be sure
that no one of them will be re-started.

## References
- https://git.kernel.org/stable/c/019ca2804f3fb49a7f8e56ea6aeaa1ff32724c27
- https://git.kernel.org/stable/c/2c5081439c7ab8da08427befe427f0d732ebc9f9
- https://git.kernel.org/stable/c/3e6429e3707943078240a2c0c0b3ee99ea9b0d9c
- https://git.kernel.org/stable/c/571ce6b6f5cbaf7d24af03cad592fc0e2a54de35
- https://git.kernel.org/stable/c/6815846e0c3a62116a7da9740e3a7c10edc5c7e9
- https://git.kernel.org/stable/c/7f533cc5ee4c4436cee51dc58e81dfd9c3384418
- https://git.kernel.org/stable/c/87389bff743c55b6b85282de91109391f43e0814
- https://git.kernel.org/stable/c/fe8421e853ef289e1324fcda004751c89dd9c18a
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38075.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38075
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
