# [H] smb: client: fix deadlock in smb2_find_smb_tcon()

## Summary
Severity: High
Advisory: CVE-2024-39468
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-06-25
Source: https://osv.dev/vulnerability/CVE-2024-39468
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.162, >=5.16.0 <6.1.94, >=6.2.0 <6.6.34, >=6.7.0 <6.9.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: fix deadlock in smb2_find_smb_tcon()

Unlock cifs_tcp_ses_lock before calling cifs_put_smb_ses() to avoid such
deadlock.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-355557.html
- https://cert-portal.siemens.com/productcert/html/ssa-613116.html
- https://git.kernel.org/stable/c/02c418774f76a0a36a6195c9dbf8971eb4130a15
- https://git.kernel.org/stable/c/21f5dd36e655d25a7b45b61c1e537198b671f720
- https://git.kernel.org/stable/c/225de871ddf994f69a57f035709cad9c0ab8615a
- https://git.kernel.org/stable/c/8d0f5f1ccf675454a833a573c53830a49b7d1a47
- https://git.kernel.org/stable/c/b055752675cd1d1db4ac9c2750db3dc3e89ea261
- https://git.kernel.org/stable/c/b09b556e48968317887a11243a5331a7bc00ece5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39468.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-39468
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
