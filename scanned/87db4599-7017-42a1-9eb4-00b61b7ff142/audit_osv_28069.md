# [H] nvme: host: fix double-free of struct nvme_id_ns in ns_update_nuse()

## Summary
Severity: High
Advisory: CVE-2024-27392
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-27392
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.8.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvme: host: fix double-free of struct nvme_id_ns in ns_update_nuse()

When nvme_identify_ns() fails, it frees the pointer to the struct
nvme_id_ns before it returns. However, ns_update_nuse() calls kfree()
for the pointer even when nvme_identify_ns() fails. This results in
KASAN double-free, which was observed with blktests nvme/045 with
proposed patches [1] on the kernel v6.8-rc7. Fix the double-free by
skipping kfree() when nvme_identify_ns() fails.

## References
- https://git.kernel.org/stable/c/534f9dc7fe495b3f9cc84363898ac50c5a25fccb
- https://git.kernel.org/stable/c/8d0d2447394b13fb22a069f0330f9c49b7fff9d3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27392.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27392
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
