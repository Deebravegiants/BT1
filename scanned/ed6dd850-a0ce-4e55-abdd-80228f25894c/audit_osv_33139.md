# [H] soc: qcom: mdt_loader: Ensure we don't read past the ELF header

## Summary
Severity: High
Advisory: CVE-2025-39787
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-11
Source: https://osv.dev/vulnerability/CVE-2025-39787
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <5.4.297, >=5.5.0 <5.10.241, >=5.11.0 <5.15.190, >=5.16.0 <6.1.149, >=6.2.0 <6.6.103, >=6.7.0 <6.12.44, >=6.13.0 <6.16.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

soc: qcom: mdt_loader: Ensure we don't read past the ELF header

When the MDT loader is used in remoteproc, the ELF header is sanitized
beforehand, but that's not necessary the case for other clients.

Validate the size of the firmware buffer to ensure that we don't read
past the end as we iterate over the header. e_phentsize and e_shentsize
are validated as well, to ensure that the assumptions about step size in
the traversal are valid.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/0d59ce2bfc3bb13abe6240335a1bf7b96536d022
- https://git.kernel.org/stable/c/1096eb63ecfc8df90b70cd068e6de0c2ff204dfd
- https://git.kernel.org/stable/c/43d26997d88c4056fce0324e72f62556bc7e8e8d
- https://git.kernel.org/stable/c/81278be4eb5f08ba2c68c3055893e61cc03727fe
- https://git.kernel.org/stable/c/87bfabb3b2f46827639173f143aa43f7cfc0a7e6
- https://git.kernel.org/stable/c/981c845f29838e468a9bfa87f784307193a31297
- https://git.kernel.org/stable/c/9f9967fed9d066ed3dae9372b45ffa4f6fccfeef
- https://git.kernel.org/stable/c/e1720eb32acf411c328af6a8c8f556c94535808e
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39787.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39787
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
