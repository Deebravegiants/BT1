# [H] ASoC: rt5645: Fix errorenous cleanup order

## Summary
Severity: High
Advisory: CVE-2022-49493
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49493
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.13.0 <4.14.283, >=4.15.0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: rt5645: Fix errorenous cleanup order

There is a logic error when removing rt5645 device as the function
rt5645_i2c_remove() first cancel the &rt5645->jack_detect_work and
delete the &rt5645->btn_check_timer latter. However, since the timer
handler rt5645_btn_check_callback() will re-queue the jack_detect_work,
this cleanup order is buggy.

That is, once the del_timer_sync in rt5645_i2c_remove is concurrently
run with the rt5645_btn_check_callback, the canceled jack_detect_work
will be rescheduled again, leading to possible use-after-free.

This patch fix the issue by placing the del_timer_sync function before
the cancel_delayed_work_sync.

## References
- https://git.kernel.org/stable/c/061a6159cea583f1155f67d1915917a6b9282662
- https://git.kernel.org/stable/c/0941150100173d4eaf3fe08ff4b16740e7c3026f
- https://git.kernel.org/stable/c/1a5a3dfd9f172dcb115072f0aea5e27d3083c20e
- https://git.kernel.org/stable/c/236d29c5857f02e0a53fdf15d3dce1536c4322ce
- https://git.kernel.org/stable/c/2def44d3aec59e38d2701c568d65540783f90f2f
- https://git.kernel.org/stable/c/453f0920ffc1a28e28ddb9c3cd5562472b2895b0
- https://git.kernel.org/stable/c/88c09e4812d72c3153afc8e5a45ecac2d0eae3ff
- https://git.kernel.org/stable/c/abe7554da62cb489712a54de69ef5665c250e564
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49493.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49493
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
