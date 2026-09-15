# [H] staging: rtl8723bs: initialize le_tmp64 in rtw_BIP_verify()

## Summary
Severity: High
Advisory: CVE-2026-31626
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31626
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.136, >=6.7.0 <6.12.83, >=6.13.0 <6.18.24, >=6.19.0 <6.19.14, >=6.20.0 <7.0.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

staging: rtl8723bs: initialize le_tmp64 in rtw_BIP_verify()

Initialize le_tmp64 to zero in rtw_BIP_verify() to prevent using
uninitialized data.

Smatch warns that only 6 bytes are copied to this 8-byte (u64)
variable, leaving the last two bytes uninitialized:

drivers/staging/rtl8723bs/core/rtw_security.c:1308 rtw_BIP_verify()
warn: not copying enough bytes for '&le_tmp64' (8 vs 6 bytes)

Initializing the variable at the start of the function fixes this
warning and ensures predictable behavior.

## References
- https://git.kernel.org/stable/c/51532c7c1d357145f4ac561648499f7a6847f739
- https://git.kernel.org/stable/c/6792624d933146e2757b07092e93ad915cb58930
- https://git.kernel.org/stable/c/8c964b82a4e97ec7f25e17b803ee196009b38a57
- https://git.kernel.org/stable/c/9e911eead187240193516edf55a0e1ab3425aa5b
- https://git.kernel.org/stable/c/b487a7754d874230299d5a9c2710ec4df8b2ed8a
- https://git.kernel.org/stable/c/c2026c6b603ebec52f55015496703fe79077accf
- https://git.kernel.org/stable/c/c65ee4d3be5df395e48afbcd0946dd5fce4338a9
- https://git.kernel.org/stable/c/d5b8f5f8d6fc09a8af5ed139c688660f578ed732
- https://git.kernel.org/stable/c/ef74ce5f0bc0e53ce702d8a794f3957884a26efc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31626.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31626
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
