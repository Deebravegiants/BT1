# [H] ASoC: SOF: ipc4-topology: Harden loops for looking up ALH copiers

## Summary
Severity: High
Advisory: CVE-2025-21870
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2025-21870
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.12.17, >=6.13.0 <6.13.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: SOF: ipc4-topology: Harden loops for looking up ALH copiers

Other, non DAI copier widgets could have the same  stream name (sname) as
the ALH copier and in that case the copier->data is NULL, no alh_data is
attached, which could lead to NULL pointer dereference.
We could check for this NULL pointer in sof_ipc4_prepare_copier_module()
and avoid the crash, but a similar loop in sof_ipc4_widget_setup_comp_dai()
will miscalculate the ALH device count, causing broken audio.

The correct fix is to harden the matching logic by making sure that the
1. widget is a DAI widget - so dai = w->private is valid
2. the dai (and thus the copier) is ALH copier

## References
- https://git.kernel.org/stable/c/6fd60136d256b3b948333ebdb3835f41a95ab7ef
- https://git.kernel.org/stable/c/87c8768a96092ce75cd47fe076db5080db7ac515
- https://git.kernel.org/stable/c/93c6c2e5801aab09ef1ef99f248f3cd323c3f152
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21870.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21870
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
