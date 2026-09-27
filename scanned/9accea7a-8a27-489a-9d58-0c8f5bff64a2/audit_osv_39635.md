# [H] net/sched: fix pedit partial COW leading to page cache corruption

## Summary
Severity: High
Advisory: CVE-2026-46331
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-16
Source: https://osv.dev/vulnerability/CVE-2026-46331
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.260, >=5.11.0 <5.15.211, >=5.16.0 <6.1.177, >=5.18.0 <6.6.144, >=6.2.0 <6.12.94, >=6.7.0 <6.18.36, >=6.13.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/sched: fix pedit partial COW leading to page cache corruption

tcf_pedit_act() computes the COW range for skb_ensure_writable()
once before the key loop using tcfp_off_max_hint, but the hint does
not account for the runtime header offset added by typed keys. This
can leave part of the write region un-COW'd.

Fix by moving skb_ensure_writable() inside the per-key loop where
the actual write offset is known, and add overflow checking on the
offset arithmetic. For negative offsets (e.g. Ethernet header edits
at ingress), use skb_cow() to COW the headroom instead. Guard
offset_valid() against INT_MIN, where negation is undefined.

## References
- https://git.kernel.org/stable/c/2bec122b9fb91507a758ab5e3e5c4fbe7cb3f61b
- https://git.kernel.org/stable/c/3dee9d0c198faeb95d052c1b94c2958751a28512
- https://git.kernel.org/stable/c/544d857b42a1734b923040e13aa61a6fd4746cf2
- https://git.kernel.org/stable/c/899ee91156e57784090c5565e4f31bd7dbffbc5a
- https://git.kernel.org/stable/c/a071e057518decc5e3bec89855758f5f8786f2c5
- https://git.kernel.org/stable/c/b198ed4e52580a7238c7c7082f03906f8b310313
- https://git.kernel.org/stable/c/b685d6ef6f07a3b5ce814565a25f39f2157538a5
- https://git.kernel.org/stable/c/d5d01d35a5a7d36f7cb679b67d9cbdd5205672dc
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-46331.json
- https://access.redhat.com/errata/RHSA-2026:27288
- https://access.redhat.com/errata/RHSA-2026:27353
- https://access.redhat.com/errata/RHSA-2026:27354
- https://access.redhat.com/errata/RHSA-2026:27355
- https://access.redhat.com/errata/RHSA-2026:27704
- https://access.redhat.com/errata/RHSA-2026:27705
- https://access.redhat.com/errata/RHSA-2026:27706
- https://access.redhat.com/errata/RHSA-2026:27707
- https://access.redhat.com/errata/RHSA-2026:27708
- https://access.redhat.com/errata/RHSA-2026:27709
- https://access.redhat.com/errata/RHSA-2026:27713
