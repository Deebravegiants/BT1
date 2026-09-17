# [M] xtensa: Fix refcount leak bug in time.c

## Summary
Severity: Medium
Advisory: CVE-2022-49682
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49682
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <4.9.321, >=4.10.0 <4.14.286, >=4.15.0 <4.19.250, >=4.20.0 <5.4.202, >=5.5.0 <5.10.127, >=5.11.0 <5.15.51, >=5.16.0 <5.18.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

xtensa: Fix refcount leak bug in time.c

In calibrate_ccount(), of_find_compatible_node() will return a node
pointer with refcount incremented. We should use of_node_put() when
it is not used anymore.

## References
- https://git.kernel.org/stable/c/0dcc1dd8a5dd9240639f1051dfaa2dffc9fbbde5
- https://git.kernel.org/stable/c/0e403a383c14b63c86bd9df085b7e573e9caee64
- https://git.kernel.org/stable/c/3e5eb904d9ba657308fc75a5de434b0e58dcb8d7
- https://git.kernel.org/stable/c/7de4502af68f4f3932f450157f5483eb7b33cb74
- https://git.kernel.org/stable/c/a0117dc956429f2ede17b323046e1968d1849150
- https://git.kernel.org/stable/c/af0ff2da01521144bc11194f4c26485d7c9cee73
- https://git.kernel.org/stable/c/e5234a9d64a976abd134a14710dcd5188158a7c5
- https://git.kernel.org/stable/c/f1eaf4ba5372ad111f687a80c67e270708e14c23
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49682.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49682
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
