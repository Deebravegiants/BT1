# [M] powerpc/fsl_rio: Fix refcount leak in fsl_rio_setup

## Summary
Severity: Medium
Advisory: CVE-2022-49439
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49439
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.3.0 <4.14.283, >=4.15.0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

powerpc/fsl_rio: Fix refcount leak in fsl_rio_setup

of_parse_phandle() returns a node pointer with refcount
incremented, we should use of_node_put() on it when not need anymore.
Add missing of_node_put() to avoid refcount leak.

## References
- https://git.kernel.org/stable/c/46fd994763cf6884b88a2da712af918f3ed54d7b
- https://git.kernel.org/stable/c/51e25fbf20c9152d84a34b7afac15a41fe5c9116
- https://git.kernel.org/stable/c/5607a77a365df8c0fd5ff43ac424812b95775527
- https://git.kernel.org/stable/c/5b8aa2ba38c010f47c965dd9bb5a8561813ed649
- https://git.kernel.org/stable/c/7b668a59ddfb32727e39b06fdf52b28e58c684e0
- https://git.kernel.org/stable/c/bcb6c4c5eb4836a21411dfe8247bf9951eb6e7c3
- https://git.kernel.org/stable/c/c70dd353d37158e06bf8d450d4b31a7091609924
- https://git.kernel.org/stable/c/fcee96924ba1596ca80a6770b2567ca546f9a482
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49439.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49439
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
