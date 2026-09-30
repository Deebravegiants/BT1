# [H] can: bcm: add missing rcu list annotations and operations

## Summary
Severity: High
Advisory: CVE-2026-72120
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72120
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.15.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: bcm: add missing rcu list annotations and operations

sashiko-bot remarked the missing use of list_add_rcu() in
bcm_[rx|tx]_setup() to have a proper initialized bcm_op structure
when bcm_proc_show() traverses the bcm_op's under rcu_read_lock().

To cover all initial settings of the bcm_op's the list_add_rcu() calls
are moved to the end of the setup code.

While at it, also fix the mirroring removal side: bcm_release() called
bcm_remove_op() - which frees the op via call_rcu() - on ops that were
still linked in bo->tx_ops/bo->rx_ops, without list_del_rcu() first.
Unlink each op with list_del_rcu() before handing it to bcm_remove_op(),
matching the existing pattern in bcm_delete_tx_op()/bcm_delete_rx_op().

## References
- https://git.kernel.org/stable/c/30f7bb922cb7e7f072a56c7cb7a5efccd2ceca1d
- https://git.kernel.org/stable/c/4e22e8b505f877573bbdfdbcb680babad9b2f7a1
- https://git.kernel.org/stable/c/7b2c3eabc4dafc062a25e10711154f2107526a78
- https://git.kernel.org/stable/c/8357255e56dc1aaa437e3c53ee9385de984e0d57
- https://git.kernel.org/stable/c/8e1c7257c81577130f5ce90f69b2a2c3ce63f957
- https://git.kernel.org/stable/c/b06a4a397ac826603f39875cb7c7819a41365196
- https://git.kernel.org/stable/c/eb1c26eab4d1f0b4450439b4b88c3e73faf1da98
- https://git.kernel.org/stable/c/f53bdab85e64eb57d6899a30d1307fd5a3639cc7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72120.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72120
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
