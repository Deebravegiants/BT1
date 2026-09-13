# [M] pinctrl: nomadik: Add missing of_node_put() in nmk_pinctrl_probe

## Summary
Severity: Medium
Advisory: CVE-2022-49185
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49185
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.9.0 <4.9.311, >=4.10.0 <4.14.276, >=4.15.0 <4.19.238, >=4.20.0 <5.4.189, >=5.5.0 <5.10.110, >=5.11.0 <5.15.33, >=5.16.0 <5.16.19, >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

pinctrl: nomadik: Add missing of_node_put() in nmk_pinctrl_probe

This node pointer is returned by of_parse_phandle() with refcount
incremented in this function. Calling of_node_put() to avoid
the refcount leak.

## References
- https://git.kernel.org/stable/c/0067ba448f1c29ca06e5aee00d8506889ed1f9d0
- https://git.kernel.org/stable/c/0356d4b64a03d23daf99a2a29d7d7d91d6ec2ea8
- https://git.kernel.org/stable/c/59250d547542f1c7765a78dc97ddfe5e6b0d2ab0
- https://git.kernel.org/stable/c/62580a40c9bef3d8a90629c64dda381344b35ffd
- https://git.kernel.org/stable/c/669b05ff43bd7ed684379c6e2006a6dad5127b71
- https://git.kernel.org/stable/c/9511c6018cd772668def8b034bc67269847e591a
- https://git.kernel.org/stable/c/bc1e29a35147c1ba6ea2b06a16cb0028f7c852d2
- https://git.kernel.org/stable/c/c09ac191b1f97cfa06f394dbfd7a5db07986cefc
- https://git.kernel.org/stable/c/c52703355766c347f270df222a744e0c491a02f2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49185.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49185
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
