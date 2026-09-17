# [M] watchdog: ts4800_wdt: Fix refcount leak in ts4800_wdt_probe

## Summary
Severity: Medium
Advisory: CVE-2022-49373
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49373
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.5.0 <5.4.198, >=5.5.0 <5.10.122, >=5.11.0 <5.15.47, >=5.16.0 <5.17.15, >=5.18.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

watchdog: ts4800_wdt: Fix refcount leak in ts4800_wdt_probe

of_parse_phandle() returns a node pointer with refcount
incremented, we should use of_node_put() on it when done.
Add  missing of_node_put() in some error paths.

## References
- https://git.kernel.org/stable/c/5b110d940417942bc87d9e4bea6d4f24e05ed483
- https://git.kernel.org/stable/c/5d24df3d690809952528e7a19a43d84bc5b99d44
- https://git.kernel.org/stable/c/7a4afd8a003d6abf1f5d159c2bb67e6b7cbde253
- https://git.kernel.org/stable/c/910b1cdf6c50ae8fb222e46657d04fb181577017
- https://git.kernel.org/stable/c/91fa5aa53f68b85e779164b3127c7e23cad5c457
- https://git.kernel.org/stable/c/f067b5286edfd83d2d3903e8578b561599d62539
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49373.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49373
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
