# [H] staging: rtl8723bs: rtw_mlme: add bounds checks before ie_length subtraction

## Summary
Severity: High
Advisory: CVE-2026-53178
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53178
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

staging: rtl8723bs: rtw_mlme: add bounds checks before ie_length subtraction

Add guards to ensure ie_length is large enough before subtracting
fixed IE offsets to prevent unsigned integer underflow.

## References
- https://git.kernel.org/stable/c/542d65a6dbd9733baab96313c9fe76a76e93f484
- https://git.kernel.org/stable/c/88e994c57a79f62d5338231d8d37ee8dd98baffe
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53178.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53178
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
