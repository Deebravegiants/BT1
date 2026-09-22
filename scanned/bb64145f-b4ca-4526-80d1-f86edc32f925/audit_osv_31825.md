# [H] smb: client: Add check for next_buffer in receive_encrypted_standard()

## Summary
Severity: High
Advisory: CVE-2025-21844
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-12
Source: https://osv.dev/vulnerability/CVE-2025-21844
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.235, >=5.11.0 <5.15.179, >=5.16.0 <6.1.130, >=6.2.0 <6.6.80, >=6.7.0 <6.13.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: Add check for next_buffer in receive_encrypted_standard()

Add check for the return value of cifs_buf_get() and cifs_small_buf_get()
in receive_encrypted_standard() to prevent null pointer dereference.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/24e8e4523d3071bc5143b0db9127d511489f7b3b
- https://git.kernel.org/stable/c/554736b583f529ee159aa95af9a0cbc12b5ffc96
- https://git.kernel.org/stable/c/860ca5e50f73c2a1cef7eefc9d39d04e275417f7
- https://git.kernel.org/stable/c/9e5d99a4cf2e23c716b44862975548415fae5391
- https://git.kernel.org/stable/c/a9b0b4b29877cb4dc5d0842b59b5ccbacddb85bd
- https://git.kernel.org/stable/c/f277e479eea3d1aa18bc712abe1d2bf3dece2e30
- https://git.kernel.org/stable/c/f618aeb6cad2307e48a641379db610abcf593edf
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21844.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21844
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
