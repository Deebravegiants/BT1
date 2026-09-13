# [H] seg6: validate SRH length before reading fixed fields

## Summary
Severity: High
Advisory: CVE-2026-72400
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72400
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.18.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

seg6: validate SRH length before reading fixed fields

seg6_validate_srh() reads fixed SRH fields such as srh->type and
srh->hdrlen before checking that the supplied length covers the fixed
struct ipv6_sr_hdr fields.

The BPF SEG6 encap path reaches this with a BPF program-supplied pointer
and length: bpf_lwt_push_encap() and the SEG6 local BPF END_B6 and
END_B6_ENCAP actions call bpf_push_seg6_encap(), which forwards the
length to seg6_validate_srh() with no minimum-size guard.  A 2-byte SEG6
encap header can therefore make the validator read srh->type at offset 2
beyond the caller-supplied buffer.

Reject lengths shorter than the fixed SRH at the top of
seg6_validate_srh(), before any field is read.  This fixes the BPF helper
path and keeps the common validator robust.

## References
- https://git.kernel.org/stable/c/071f1a38d7ddbadee29c09b9e3ee0ff3a61e6a0e
- https://git.kernel.org/stable/c/0fc7069d39239978130c37ebceaec85c8948d3f1
- https://git.kernel.org/stable/c/715eb12e453df752f1b4baaf972c3acff0ab9402
- https://git.kernel.org/stable/c/7247d05c987c3eec4bb7c2306dbd77ecdf3b7c73
- https://git.kernel.org/stable/c/804bb969f194c93497ba632b98343794c6367fdc
- https://git.kernel.org/stable/c/8dba7a94a269b88e500aafc25ad567ef6a423698
- https://git.kernel.org/stable/c/a75d99f46bf21b45965ce39c5cfb3b8bb5ffb1aa
- https://git.kernel.org/stable/c/c9961336aa5ff83092f23e33ee86666a9dbd1b2a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72400.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72400
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
