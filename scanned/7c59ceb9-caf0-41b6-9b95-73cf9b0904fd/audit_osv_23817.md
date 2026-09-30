# [H] drm/amd/pm: fix double free in si_parse_power_table()

## Summary
Severity: High
Advisory: CVE-2022-49530
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49530
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <4.9.318, >=4.10.0 <4.14.283, >=4.15.0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/pm: fix double free in si_parse_power_table()

In function si_parse_power_table(), array adev->pm.dpm.ps and its member
is allocated. If the allocation of each member fails, the array itself
is freed and returned with an error code. However, the array is later
freed again in si_dpm_fini() function which is called when the function
returns an error.

This leads to potential double free of the array adev->pm.dpm.ps, as
well as leak of its array members, since the members are not freed in
the allocation function and the array is not nulled when freed.
In addition adev->pm.dpm.num_ps, which keeps track of the allocated
array member, is not updated until the member allocation is
successfully finished, this could also lead to either use after free,
or uninitialized variable access in si_dpm_fini().

Fix this by postponing the free of the array until si_dpm_fini() and
increment adev->pm.dpm.num_ps everytime the array member is allocated.

## References
- https://git.kernel.org/stable/c/2615464854505188f909d0c07c37a6623693b5c7
- https://git.kernel.org/stable/c/43eb9b667b95f2a31c63e8949b0d2161b9be59c3
- https://git.kernel.org/stable/c/6c5bdaa1325be7f04b79ea992ab216739192d342
- https://git.kernel.org/stable/c/a5ce7051db044290b1a95045ff03c249005a3aa4
- https://git.kernel.org/stable/c/af832028af6f44c6c45645757079c4ed6884ade5
- https://git.kernel.org/stable/c/c0e811c4ccf3b42705976285e3a94cc82dea7300
- https://git.kernel.org/stable/c/ca1ce206894dd976275c78ee38dbc19873f22de9
- https://git.kernel.org/stable/c/f3fa2becf2fc25b6ac7cf8d8b1a2e4a86b3b72bd
- https://git.kernel.org/stable/c/fd2eff8b9dcbe469c3b7bbbc7083ab5ed94de07b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49530.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49530
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
