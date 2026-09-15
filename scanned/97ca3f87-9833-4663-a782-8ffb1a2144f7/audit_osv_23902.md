# [H] ima: Fix a potential integer overflow in ima_appraise_measurement

## Summary
Severity: High
Advisory: CVE-2022-49643
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49643
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.0 <5.4.207, >=5.5.0 <5.10.132, >=5.11.0 <5.15.56, >=5.16.0 <5.18.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

ima: Fix a potential integer overflow in ima_appraise_measurement

When the ima-modsig is enabled, the rc passed to evm_verifyxattr() may be
negative, which may cause the integer overflow problem.

## References
- https://git.kernel.org/stable/c/388f3df7c3c8b7f2a32b9ae0a9b2f9f6ad3b1b77
- https://git.kernel.org/stable/c/640cea4c2839a821adfbb703b590a5928abe9286
- https://git.kernel.org/stable/c/831e190175f10652be93b08436cc7bf2e62e4bb6
- https://git.kernel.org/stable/c/c8d5d81940938b5f6c0f495ca9538e7740416f30
- https://git.kernel.org/stable/c/d2ee2cfc4aa85ff6a2a3b198a3a524ec54e3d999
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49643.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49643
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
