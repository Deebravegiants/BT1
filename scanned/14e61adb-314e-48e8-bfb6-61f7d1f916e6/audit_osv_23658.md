# [M] USB: host: isp116x: check return value after calling platform_get_resource()

## Summary
Severity: Medium
Advisory: CVE-2022-49302
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49302
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.13 <4.9.318, >=4.10.0 <4.14.283, >=4.15.0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.122, >=5.11.0 <5.15.47, >=5.16.0 <5.17.15, >=5.18.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

USB: host: isp116x: check return value after calling platform_get_resource()

It will cause null-ptr-deref if platform_get_resource() returns NULL,
we need check the return value.

## References
- https://git.kernel.org/stable/c/134a3408c2d3f7e23eb0e4556e0a2d9f36c2614e
- https://git.kernel.org/stable/c/3592cfd8b848bf0c4d7740d78a87a7b8f6e1fa9a
- https://git.kernel.org/stable/c/3825db88d8c704e7992b685618a03f82bffcf2ef
- https://git.kernel.org/stable/c/7bffda1560a6f255fdf504e059fbbdb5d46b9e44
- https://git.kernel.org/stable/c/804de302ada3544699c5f48c5314b249af76faa3
- https://git.kernel.org/stable/c/82a101f14943f479fd190b1e5b40d91c77e2ac1b
- https://git.kernel.org/stable/c/aca0cab0e9ed33b6371aafb519a6c38f2850ffc3
- https://git.kernel.org/stable/c/c91a74b1f0f2d2d7e728742ae55e3ffe9ba7853d
- https://git.kernel.org/stable/c/ee105039d3653444de4d3ede642383c92855dc1e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49302.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49302
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
