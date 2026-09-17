# [M] misc: tifm: fix possible memory leak in tifm_7xx1_switch_media()

## Summary
Severity: Medium
Advisory: CVE-2022-50349
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2022-50349
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.22 <4.9.337, >=4.10.0 <4.14.303, >=4.15.0 <4.19.270, >=4.20.0 <5.4.229, >=5.5.0 <5.10.163, >=5.11.0 <5.15.86, >=5.16.0 <6.0.16, >=6.1.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

misc: tifm: fix possible memory leak in tifm_7xx1_switch_media()

If device_register() returns error in tifm_7xx1_switch_media(),
name of kobject which is allocated in dev_set_name() called in device_add()
is leaked.

Never directly free @dev after calling device_register(), even
if it returned an error! Always use put_device() to give up the
reference initialized.

## References
- https://git.kernel.org/stable/c/1695b1adcc3a7d985cd22fa3b55761edf3fab50d
- https://git.kernel.org/stable/c/2bbb222a54ff501f77ce593d21b76b79c905045e
- https://git.kernel.org/stable/c/35abbc8406cc39e72d3ce85f6e869555afe50d54
- https://git.kernel.org/stable/c/57c857353d5020bdec8284d9c0fee447484fe5e0
- https://git.kernel.org/stable/c/848c45964ded537107e010aaf353aa30a0855387
- https://git.kernel.org/stable/c/d861b7d41b17942b337d4b87a70de7cd1dc44d4e
- https://git.kernel.org/stable/c/ee2715faf7e7153f5142ed09aacfa89a64d45dcb
- https://git.kernel.org/stable/c/ef843ee20576039126d34d6eb5f45d14c3e6ce18
- https://git.kernel.org/stable/c/fd2c930cf6a5b9176382c15f9acb1996e76e25ad
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50349.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50349
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
