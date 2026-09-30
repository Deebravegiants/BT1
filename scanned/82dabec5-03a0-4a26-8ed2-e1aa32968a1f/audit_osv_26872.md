# [H] ksmbd: avoid out of bounds access in decode_preauth_ctxt()

## Summary
Severity: High
Advisory: CVE-2023-54250
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2025-12-30
Source: https://osv.dev/vulnerability/CVE-2023-54250
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.145, >=5.16.0 <6.1.25, >=6.2.0 <6.2.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: avoid out of bounds access in decode_preauth_ctxt()

Confirm that the accessed pneg_ctxt->HashAlgorithms address sits within
the SMB request boundary; deassemble_neg_contexts() only checks that the
eight byte smb2_neg_context header + (client controlled) DataLength are
within the packet boundary, which is insufficient.

Checking for sizeof(struct smb2_preauth_neg_context) is overkill given
that the type currently assumes SMB311_SALT_SIZE bytes of trailing Salt.

## References
- https://git.kernel.org/stable/c/39f5b4b313b445c980a2a295bed28228c29228ed
- https://git.kernel.org/stable/c/a2f6ded41bec1d3be643c80a5eb97f1680309001
- https://git.kernel.org/stable/c/e7067a446264a7514fa1cfaa4052cdb6803bc6a2
- https://git.kernel.org/stable/c/f02edb9debbd36f44efa7567031485892c7df60d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54250.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54250
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
