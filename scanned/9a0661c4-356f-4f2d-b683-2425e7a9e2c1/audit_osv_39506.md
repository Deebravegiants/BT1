# [H] erofs: fix unsigned underflow in z_erofs_lz4_handle_overlap()

## Summary
Severity: High
Advisory: CVE-2026-45999
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-45999
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.140, >=6.7.0 <6.12.88, >=6.13.0 <6.18.30, >=6.19.0 <7.0.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

erofs: fix unsigned underflow in z_erofs_lz4_handle_overlap()

Some crafted images can have illegal (!partial_decoding &&
m_llen < m_plen) extents, and the LZ4 inplace decompression path
can be wrongly hit, but it cannot handle (outpages < inpages)
properly: "outpages - inpages" wraps to a large value and
the subsequent rq->out[] access reads past the decompressed_pages
array.

However, such crafted cases can correctly result in a corruption
report in the normal LZ4 non-inplace path.

Let's add an additional check to fix this for backporting.

Reproducible image (base64-encoded gzipped blob):

H4sIAJGR12kCA+3SPUoDQRgG4MkmkkZk8QRbRFIIi9hbpEjrHQI5ghfwCN5BLCzTGtLbBI+g
dilSJo1CnIm7GEXFxhT6PDDwfrs73/ywIQD/1ePD4r7Ou6ETsrq4mu7XcWfj++Pb58nJU/9i
PNtbjhan04/9GtX4qVYc814WDqt6FaX5s+ZwXXeq52lndT6IuVvlblytLMvh4Gzwaf90nsvz
2DF/21+20T/ldgp5s1jXRaN4t/8izsy/OUB6e/Qa79r+JwAAAAAAAL52vQVuGQAAAP6+my1w
ywAAAAAAAADwu14ATsEYtgBQAAA=

$ mount -t erofs -o cache_strategy=disabled foo.erofs /mnt
$ dd if=/mnt/data of=/dev/null bs=4096 count=1

## References
- https://git.kernel.org/stable/c/118ff71ff09ebaf323a09af9e911517321a299f4
- https://git.kernel.org/stable/c/21e161de2dc660b1bb70ef5b156ab8e6e1cca3ab
- https://git.kernel.org/stable/c/43a878639b90e9721ffa5eb616a7e6d8454adef3
- https://git.kernel.org/stable/c/778acd52e9497806fbd2cea7f770c41d6850fc48
- https://git.kernel.org/stable/c/bbbbb3f0d7864238a8da2a94cd6ec013fee06a2e
- https://git.kernel.org/stable/c/c9ce18e6bb2c467ec85756dc7989b547b7584fee
- https://git.kernel.org/stable/c/f1374fa6e57fd836623668d782ded9244cfd2938
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45999.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-45999
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
