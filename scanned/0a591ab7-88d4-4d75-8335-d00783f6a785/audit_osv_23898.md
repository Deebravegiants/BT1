# [M] icmp: Fix data-races around sysctl.

## Summary
Severity: Medium
Advisory: CVE-2022-49638
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49638
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.18.0 <4.9.324, >=4.10.0 <4.14.289, >=4.15.0 <4.19.253, >=4.20.0 <5.4.207, >=5.5.0 <5.10.132, >=5.11.0 <5.15.56, >=5.16.0 <5.18.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

icmp: Fix data-races around sysctl.

While reading icmp sysctl variables, they can be changed concurrently.
So, we need to add READ_ONCE() to avoid data-races.

## References
- https://git.kernel.org/stable/c/0cba7ca667ceb06934746ddd9833a25847bde81d
- https://git.kernel.org/stable/c/1740e5922fbb705637ae9fa5203db132fc45f9f6
- https://git.kernel.org/stable/c/48d7ee321ea5182c6a70782aa186422a70e67e22
- https://git.kernel.org/stable/c/53ecd09ef2fb35fa69667ae8e414ef6b00fd3bf6
- https://git.kernel.org/stable/c/798c2cf57c63ab39c8aac24d6a3d50f4fa5eeb06
- https://git.kernel.org/stable/c/e088ceb73c24ab4774da391d54a6426f4bfaefce
- https://git.kernel.org/stable/c/e2828e8c605853f71267825c9415437c0a93e4f2
- https://git.kernel.org/stable/c/edeec63b13c252193d626c2a48d7a2f0e7016dc2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49638.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49638
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
