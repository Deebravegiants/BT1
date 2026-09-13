# [H] vhost-scsi: Validate T10 PI scatterlist counts

## Summary
Severity: High
Advisory: CVE-2026-74703
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74703
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

vhost-scsi: Validate T10 PI scatterlist counts

When T10 PI is negotiated, vhost-scsi splits protection bytes from
the data iterator before mapping the request scatterlists. A malformed
request can claim protection bytes that cover or exceed the full payload
length. The former leaves no data bytes to map, while the latter
underflows exp_data_len before advancing the iterator. Both cases can let
a zero data SGL count reach sg_alloc_table_chained(), which triggers
BUG_ON(!nents).

Reject protection lengths that cover or exceed the payload before
subtracting prot_bytes and advancing the iterator. Also propagate
negative errors from the protection SGL calculation before calling the
allocator, matching the data SGL path.

## References
- https://git.kernel.org/stable/c/2417a498cf3fe64d06faf87e236eda98dd4f04e0
- https://git.kernel.org/stable/c/d876c493fc4b811941bfeb4c80beb2dfc4bf025e
- https://git.kernel.org/stable/c/f8fe3f8d342da750dd10361bf66009fd3072926b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74703.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74703
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
