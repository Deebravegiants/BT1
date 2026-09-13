# [H] ALSA: ac97: fix a double free in snd_ac97_controller_register()

## Summary
Severity: High
Advisory: CVE-2025-71192
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-04
Source: https://osv.dev/vulnerability/CVE-2025-71192
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <6.1.161, >=6.2.0 <6.6.121, >=6.7.0 <6.12.66, >=6.13.0 <6.18.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: ac97: fix a double free in snd_ac97_controller_register()

If ac97_add_adapter() fails, put_device() is the correct way to drop
the device reference. kfree() is not required.
Add kfree() if idr_alloc() fails and in ac97_adapter_release() to do
the cleanup.

Found by code review.

## References
- https://git.kernel.org/stable/c/21f8bc5179bed91c3f946adb5e55d717b891960c
- https://git.kernel.org/stable/c/830988b6cf197e6dcffdfe2008c5738e6c6c3c0f
- https://git.kernel.org/stable/c/c80f9b3349a99a9d5b295f5bbc23f544c5995ad7
- https://git.kernel.org/stable/c/cb73d37ac18bc1716690ff5255a0ef1952827e9e
- https://git.kernel.org/stable/c/fcc04c92cbb5497ce67c58dd2f0001bb87f40396
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71192.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-71192
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
