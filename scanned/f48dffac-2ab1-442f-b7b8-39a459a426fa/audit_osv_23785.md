# [M] ASoC: mxs-saif: Fix refcount leak in mxs_saif_probe

## Summary
Severity: Medium
Advisory: CVE-2022-49482
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49482
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.5.0 <4.9.318, >=4.10.0 <4.14.283, >=4.15.0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: mxs-saif: Fix refcount leak in mxs_saif_probe

of_parse_phandle() returns a node pointer with refcount
incremented, we should use of_node_put() on it when done.

## References
- https://git.kernel.org/stable/c/18b907ff0ae4bf20120aae1538f7156b9d08e3a7
- https://git.kernel.org/stable/c/24491124406666bf0dcb9ee10c5575c6ce6a1730
- https://git.kernel.org/stable/c/2a0da7641e1f17a744ac7b3f76471388c97b63dc
- https://git.kernel.org/stable/c/2be84f73785fa9ed6443e3c5b158730266f1c2ee
- https://git.kernel.org/stable/c/30d110ca703ce60162ec337aa564a3e4da30715f
- https://git.kernel.org/stable/c/4e2a1bcc51bdebed48176f6e88c150f175983f9c
- https://git.kernel.org/stable/c/c933829cbf3338b684869e6c4c8931abf5d68fbd
- https://git.kernel.org/stable/c/d42601e93fce7802bb8d70dd59b60cfeefa20469
- https://git.kernel.org/stable/c/d855505851ee8ba666eb204149b49f906130dc17
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49482.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49482
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
