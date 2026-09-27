# [M] net: hinic: fix the issue of CMDQ memory leaks

## Summary
Severity: Medium
Advisory: CVE-2022-50387
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2022-50387
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.10.153, >=5.11.0 <5.15.77, >=5.16.0 <6.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: hinic: fix the issue of CMDQ memory leaks

When hinic_set_cmdq_depth() fails in hinic_init_cmdqs(), the cmdq memory is
not released correctly. Fix it.

## References
- https://git.kernel.org/stable/c/363cc87767f6ddcfb9158ad2e2afa2f8d5c4b94e
- https://git.kernel.org/stable/c/6016d96a6adf66d61655d85da02e1a4c1deccbd6
- https://git.kernel.org/stable/c/6603843c80b16957f5d7d14d897faf13cef2b8b9
- https://git.kernel.org/stable/c/9145d512ddff76df88832b29575488199df544a1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50387.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50387
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
