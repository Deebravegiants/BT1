# [M] media: rga: fix possible memory leak in rga_probe

## Summary
Severity: Medium
Advisory: CVE-2022-49502
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49502
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: rga: fix possible memory leak in rga_probe

rga->m2m_dev needs to be freed when rga_probe fails.

## References
- https://git.kernel.org/stable/c/1cdc768468c25d6b10ab83ec1efd4a8554532d69
- https://git.kernel.org/stable/c/8ddc89437ccefa18279918c19a61fd81527f40b9
- https://git.kernel.org/stable/c/a71eb6025305192e646040cd76ccacb5bd48a1b5
- https://git.kernel.org/stable/c/b7bbca4d08471bc8404a946bab1aa017dd05199b
- https://git.kernel.org/stable/c/eeb4819e94aa69767b9e5591e70c63e8b7c5786a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49502.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49502
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
