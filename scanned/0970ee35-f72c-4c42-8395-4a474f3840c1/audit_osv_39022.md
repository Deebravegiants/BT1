# [H] ksmbd: Don't log keys in SMB3 signing and encryption key generation

## Summary
Severity: High
Advisory: CVE-2026-43377
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43377
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.1.167, >=6.2.0 <6.6.130, >=6.7.0 <6.12.78, >=6.13.0 <6.18.20, >=6.19.0 <6.19.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: Don't log keys in SMB3 signing and encryption key generation

When KSMBD_DEBUG_AUTH logging is enabled, generate_smb3signingkey() and
generate_smb3encryptionkey() log the session, signing, encryption, and
decryption key bytes. Remove the logs to avoid exposing credentials.

## References
- https://git.kernel.org/stable/c/3fe2d9ec166b7df9a8df6c0fdcfc210572e27e3f
- https://git.kernel.org/stable/c/407cc37c21d51f9b9d4d20204b04890880cfa6ae
- https://git.kernel.org/stable/c/4084ed720d7d5f4e975c9e4a6267a552dad3b24a
- https://git.kernel.org/stable/c/441336115df26b966575de56daf7107ed474faed
- https://git.kernel.org/stable/c/c6b01b997a2094969e315f1ebfc1d64b8ae2163d
- https://git.kernel.org/stable/c/fec5c70b82af3f59f15bb984df94e5ad1fccfb1e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43377.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43377
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
