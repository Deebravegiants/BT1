# [H] tcp: initialize standalone TCP-AO response padding

## Summary
Severity: High
Advisory: CVE-2026-68119
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68119
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

tcp: initialize standalone TCP-AO response padding

tcp_v4_send_ack() and tcp_v6_send_response() construct standalone TCP
responses with TCP-AO options.  The option length carries the actual MAC
length, but the TCP header length includes the option rounded up to a
four-byte boundary.

tcp_ao_hash_hdr() writes the MAC only.  Thus, when the MAC length is not
four-byte aligned, the one to three bytes after the MAC are left
uninitialized and may be transmitted.  For the normal TCP-AO hashing
mode, those bytes also have to be initialized before computing the MAC.

Initialize only the alignment padding in the TCP-AO branches, before
hashing the header.  Use TCPOPT_NOP, as in the normal TCP-AO output path.
This avoids adding work to non-AO TCP responses while preserving a valid
authenticated header.

## References
- https://git.kernel.org/stable/c/a859b280441fb02f64ed4037f03d5c0c34a7a595
- https://git.kernel.org/stable/c/bbb7db8c74b0b5d17a695136f0f0806ecd0118f6
- https://git.kernel.org/stable/c/e1a9d3cc11829c5414a75eb39c704f461936eb24
- https://git.kernel.org/stable/c/fadaff3f66e124c3a62237f9c881819a8ac90309
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68119.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68119
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
