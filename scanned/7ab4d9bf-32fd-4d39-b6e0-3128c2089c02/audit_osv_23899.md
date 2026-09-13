# [M] cipso: Fix data-races around sysctl.

## Summary
Severity: Medium
Advisory: CVE-2022-49639
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49639
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.19 <4.9.324, >=4.10.0 <4.14.289, >=4.15.0 <4.19.253, >=4.20.0 <5.4.207, >=5.5.0 <5.10.132, >=5.11.0 <5.15.56, >=5.16.0 <5.18.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

cipso: Fix data-races around sysctl.

While reading cipso sysctl variables, they can be changed concurrently.
So, we need to add READ_ONCE() to avoid data-races.

## References
- https://git.kernel.org/stable/c/07b0caf8aeb9b82e6ecc6c292a3e47c7fcdb1148
- https://git.kernel.org/stable/c/0e41a0f73ccb9be112a80bde3804a771633caaef
- https://git.kernel.org/stable/c/2764f82bbc158d106693ae3ced3675cf4b963b35
- https://git.kernel.org/stable/c/59e26906b89cc35bb54476498772b45cbc32323f
- https://git.kernel.org/stable/c/c321e99d2725d11f7e6a4ebd9ce752259f0bae81
- https://git.kernel.org/stable/c/ca26ca5e2f3eeb3e6fe699cd6effa3b4b2aa8698
- https://git.kernel.org/stable/c/dd44f04b9214adb68ef5684ae87a81ba03632250
- https://git.kernel.org/stable/c/fe2a35fa2c4f9c8ce5ef970eb927031387f9446a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49639.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49639
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
