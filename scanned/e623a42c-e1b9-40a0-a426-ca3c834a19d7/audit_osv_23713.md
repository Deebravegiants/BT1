# [M] rtc: mt6397: check return value after calling platform_get_resource()

## Summary
Severity: Medium
Advisory: CVE-2022-49375
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49375
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <4.9.318, >=4.10.0 <4.14.283, >=4.15.0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.122, >=5.11.0 <5.15.47, >=5.16.0 <5.17.15, >=5.18.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

rtc: mt6397: check return value after calling platform_get_resource()

It will cause null-ptr-deref if platform_get_resource() returns NULL,
we need check the return value.

## References
- https://git.kernel.org/stable/c/3867f0bbb94773d41e789257abec0d14f37da217
- https://git.kernel.org/stable/c/58a729c55ce3a432eb827fdaa24c7909cd3b0a6b
- https://git.kernel.org/stable/c/6ecd4d5c28408df36a1a6f0b1973f633c949ac1f
- https://git.kernel.org/stable/c/79fa3f5758d8712df0678df98161f948fc4370e5
- https://git.kernel.org/stable/c/82bfea344e8f7e9a0e0b1bf9af27552baa756620
- https://git.kernel.org/stable/c/865051de2d9eaa50630e055b73921ceaf3c4a7fc
- https://git.kernel.org/stable/c/d3b43eb505bffb8e4cdf6800c15660c001553fe6
- https://git.kernel.org/stable/c/d77f28c1bc9d3043a52069fe42e4a26fbf961ebd
- https://git.kernel.org/stable/c/da38e86d6cf6dd3bc65c602d998f357145aa1a0b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49375.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49375
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
