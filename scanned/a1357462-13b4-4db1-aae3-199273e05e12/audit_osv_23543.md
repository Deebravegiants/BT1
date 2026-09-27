# [M] habanalabs: fix possible memory leak in MMU DR fini

## Summary
Severity: Medium
Advisory: CVE-2022-49102
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49102
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.34, >=5.16.0 <5.16.20, >=5.17.0 <5.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

habanalabs: fix possible memory leak in MMU DR fini

This patch fixes what seems to be copy paste error.

We will have a memory leak if the host-resident shadow is NULL (which
will likely happen as the DR and HR are not dependent).

## References
- https://git.kernel.org/stable/c/12e49aefda2e04b07604f13e03f40027cbeb0dc6
- https://git.kernel.org/stable/c/30058d3a83cfe8c6aacbfe5ab13c01dd0c1799e3
- https://git.kernel.org/stable/c/6d421fb7a9eddd8ce0a05641a3db97283fe20699
- https://git.kernel.org/stable/c/eb85eec858c1a5c11d3a0bff403f6440b05b40dc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49102.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49102
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
