# [H] crypto/krb5, rxrpc: Fix lack of pre-decrypt/pre-verify length checks

## Summary
Severity: High
Advisory: CVE-2026-64208
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-24
Source: https://osv.dev/vulnerability/CVE-2026-64208
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto/krb5, rxrpc: Fix lack of pre-decrypt/pre-verify length checks

Change the krb5 crypto library to provide facilities to precheck the length
of the message about to be decrypted or verified.

Fix AF_RXRPC to make use of this to validate DATA packets secured with
RxGK.

## References
- https://git.kernel.org/stable/c/2b50aceafe6606ea52ed42aadd1b4d44a188aade
- https://git.kernel.org/stable/c/585f9f6aef5c4542ac9d6ec45cd7dbc7df9af3ff
- https://git.kernel.org/stable/c/9217017f4bce53dddb8d547837f1f707045d64ad
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64208.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64208
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
