# [H] power: supply: rk817: Fix node refcount leak

## Summary
Severity: High
Advisory: CVE-2023-52571
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-03-02
Source: https://osv.dev/vulnerability/CVE-2023-52571
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.56, >=6.2.0 <6.5.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

power: supply: rk817: Fix node refcount leak

Dan Carpenter reports that the Smatch static checker warning has found
that there is another refcount leak in the probe function. While
of_node_put() was added in one of the return paths, it should in
fact be added for ALL return paths that return an error and at driver
removal time.

## References
- https://git.kernel.org/stable/c/488ef44c068e79752dba8eda0b75f524f111a695
- https://git.kernel.org/stable/c/70326b46b6a043f7e7404b2ff678b033c06d6577
- https://git.kernel.org/stable/c/fe6406238d5a24e9fb0286c71edd67b99d8db58d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52571.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52571
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
