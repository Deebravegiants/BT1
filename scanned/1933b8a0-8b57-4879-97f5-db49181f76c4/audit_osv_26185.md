# [C] ksmbd: fix slub overflow in ksmbd_decode_ntlmssp_auth_blob()

## Summary
Severity: Critical
Advisory: CVE-2023-52440
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-21
Source: https://osv.dev/vulnerability/CVE-2023-52440
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <6.1.52, >=6.2.0 <6.4.15, >=6.5.0 <6.5.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix slub overflow in ksmbd_decode_ntlmssp_auth_blob()

If authblob->SessionKey.Length is bigger than session key
size(CIFS_KEY_SIZE), slub overflow can happen in key exchange codes.
cifs_arc4_crypt copy to session key array from SessionKey from client.

## References
- https://git.kernel.org/stable/c/30fd6521b2fbd9b767e438e31945e5ea3e3a2fba
- https://git.kernel.org/stable/c/4b081ce0d830b684fdf967abc3696d1261387254
- https://git.kernel.org/stable/c/7f1d6cb0eb6af3a8088dc24b7ddee9a9711538c4
- https://git.kernel.org/stable/c/bd554ed4fdc3d38404a1c43d428432577573e809
- https://git.kernel.org/stable/c/ecd7e1c562cb08e41957fcd4b0e404de5ab38e20
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52440.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52440
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
