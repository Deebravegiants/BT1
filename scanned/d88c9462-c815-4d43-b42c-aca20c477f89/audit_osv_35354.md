# [H] media: adv7842: Avoid possible out-of-bounds array accesses in adv7842_cp_log_status()

## Summary
Severity: High
Advisory: CVE-2025-71136
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-01-14
Source: https://osv.dev/vulnerability/CVE-2025-71136
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.12.0 <5.10.248, >=5.11.0 <5.15.198, >=5.16.0 <6.1.160, >=6.2.0 <6.6.120, >=6.7.0 <6.12.64, >=6.13.0 <6.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: adv7842: Avoid possible out-of-bounds array accesses in adv7842_cp_log_status()

It's possible for cp_read() and hdmi_read() to return -EIO. Those
values are further used as indexes for accessing arrays.

Fix that by checking return values where it's needed.

Found by Linux Verification Center (linuxtesting.org) with SVACE.

## References
- https://git.kernel.org/stable/c/60dde0960e3ead8a9569f6c494d90d0232ac0983
- https://git.kernel.org/stable/c/8163419e3e05d71dcfa8fb49c8fdf8d76908fe51
- https://git.kernel.org/stable/c/a73881ae085db5702d8b13e2fc9f78d51c723d3f
- https://git.kernel.org/stable/c/b693d48a6ed0cd09171103ad418e4a693203d6e4
- https://git.kernel.org/stable/c/d6a22a4a96e4dfe6897cb3532d2b3016d87706f0
- https://git.kernel.org/stable/c/f81ee181cb036d046340c213091b69d9a8701a76
- https://git.kernel.org/stable/c/f913b9a2ccd6114b206b9e91dae5e3dc13a415a0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71136.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-71136
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
