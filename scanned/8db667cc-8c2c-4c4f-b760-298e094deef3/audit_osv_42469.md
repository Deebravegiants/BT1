# [H] media: vivid: check for vb2_is_busy() when toggling caps

## Summary
Severity: High
Advisory: CVE-2026-68204
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68204
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.18.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: vivid: check for vb2_is_busy() when toggling caps

The vivid_update_format_cap/out() functions must only be called if the
capture/output queue are not busy. But for the controls that select
the CROP/COMPOSE/SCALE capability that is not checked.

Only when streaming starts will they be set to 'grabbed' and it is
impossible to change the control, but between REQBUFS and STREAMON you
are still allowed to set these controls. Since vivid_update_format_cap/out
will change the format, this can cause unexpected results.

Besides adding these checks, also add a WARN_ON in
vivid_update_format_cap/out() if the queue is busy.

I'm 90% certain that this is the cause of this syzbot bug:

https://syzkaller.appspot.com/bug?extid=dac8f5eaa46837e97b89

But since we never have reproducers, it is hard to be certain. In any case,
these checks are needed regardless.

## References
- https://git.kernel.org/stable/c/0a820f03727b509b887f3216a574062948761f34
- https://git.kernel.org/stable/c/492c97cb50feaa60ccd7792d3d6b904ed8ec61bf
- https://git.kernel.org/stable/c/6a5bc8aea111ccbca71ef2b9c868d5c81f2e89de
- https://git.kernel.org/stable/c/a9cd0e8fb0b21faaa71199d9d3feb305c18ff576
- https://git.kernel.org/stable/c/abaec6747304581f8d4a9936352fa10e13325f07
- https://git.kernel.org/stable/c/bbc96bc75de0fcd9bb6ac48798b206e3b09ec865
- https://git.kernel.org/stable/c/c2d1a2130c93f6d758af58590b86b2254c7a1dec
- https://git.kernel.org/stable/c/daf2d92669b4a659d805d88d811161c70cd325ee
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68204.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68204
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
