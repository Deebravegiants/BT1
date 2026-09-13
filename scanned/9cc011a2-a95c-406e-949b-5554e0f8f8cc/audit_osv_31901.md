# [H] Revert "openvswitch: switch to per-action label counting in conntrack"

## Summary
Severity: High
Advisory: CVE-2025-21958
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-21958
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.20, >=6.13.0 <6.13.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

Revert "openvswitch: switch to per-action label counting in conntrack"

Currently, ovs_ct_set_labels() is only called for confirmed conntrack
entries (ct) within ovs_ct_commit(). However, if the conntrack entry
does not have the labels_ext extension, attempting to allocate it in
ovs_ct_get_conn_labels() for a confirmed entry triggers a warning in
nf_ct_ext_add():

  WARN_ON(nf_ct_is_confirmed(ct));

This happens when the conntrack entry is created externally before OVS
increments net->ct.labels_used. The issue has become more likely since
commit fcb1aa5163b1 ("openvswitch: switch to per-action label counting
in conntrack"), which changed to use per-action label counting and
increment net->ct.labels_used when a flow with ct action is added.

Since there’s no straightforward way to fully resolve this issue at the
moment, this reverts the commit to avoid breaking existing use cases.

## References
- https://git.kernel.org/stable/c/1063ae07383c0ddc5bcce170260c143825846b03
- https://git.kernel.org/stable/c/9e79fdabd52cfce1a021640a81256878a2c516a2
- https://git.kernel.org/stable/c/d91bfc64a4886102746e74d2c6f3a61e9a77fd7d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21958.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21958
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
