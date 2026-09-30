# [C] net/mlx5e: kTLS, Fix incorrect page refcounting

## Summary
Severity: Critical
Advisory: CVE-2024-53138
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-04
Source: https://osv.dev/vulnerability/CVE-2024-53138
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.0 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.119, >=6.2.0 <6.6.63, >=6.7.0 <6.11.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/mlx5e: kTLS, Fix incorrect page refcounting

The kTLS tx handling code is using a mix of get_page() and
page_ref_inc() APIs to increment the page reference. But on the release
path (mlx5e_ktls_tx_handle_resync_dump_comp()), only put_page() is used.

This is an issue when using pages from large folios: the get_page()
references are stored on the folio page while the page_ref_inc()
references are stored directly in the given page. On release the folio
page will be dereferenced too many times.

This was found while doing kTLS testing with sendfile() + ZC when the
served file was read from NFS on a kernel with NFS large folios support
(commit 49b29a573da8 ("nfs: add support for large folios")).

## References
- https://git.kernel.org/stable/c/2723e8b2cbd486cb96e5a61b22473f7fd62e18df
- https://git.kernel.org/stable/c/69fbd07f17b0fdaf8970bc705f5bf115c297839d
- https://git.kernel.org/stable/c/93a14620b97c911489a5b008782f3d9b0c4aeff4
- https://git.kernel.org/stable/c/a0ddb20a748b122ea86003485f7992fa5e84cc95
- https://git.kernel.org/stable/c/c7b97f9e794d8e2bbaa50e1d6c230196fd214b5e
- https://git.kernel.org/stable/c/dd6e972cc5890d91d6749bb48e3912721c4e4b25
- https://git.kernel.org/stable/c/ffad2ac8c859c1c1a981fe9c4f7ff925db684a43
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53138.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53138
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
