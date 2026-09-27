# [H] NFSD: Finish converting the NFSv2 GETACL result encoder

## Summary
Severity: High
Advisory: CVE-2022-50861
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-12-30
Source: https://osv.dev/vulnerability/CVE-2022-50861
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.86, >=5.16.0 <6.0.16, >=6.1.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFSD: Finish converting the NFSv2 GETACL result encoder

The xdr_stream conversion inadvertently left some code that set the
page_len of the send buffer. The XDR stream encoders should handle
this automatically now.

This oversight adds garbage past the end of the Reply message.
Clients typically ignore the garbage, but NFSD does not need to send
it, as it leaks stale memory contents onto the wire.

## References
- https://git.kernel.org/stable/c/2b825efb0577a32a872e872a869e0947cf9dd6d3
- https://git.kernel.org/stable/c/5030d4d2bf8b6f6f3d16401ab92a88bc5aa2377a
- https://git.kernel.org/stable/c/a20b0abab966a189a79aba6ebf41f59024a3224d
- https://git.kernel.org/stable/c/d5b867fd2d7f79630b1a2906a7bb4f4b75bf297a
- https://git.kernel.org/stable/c/ea5021e911d3479346a75ac9b7d9dcd751b0fb99
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50861.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50861
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
