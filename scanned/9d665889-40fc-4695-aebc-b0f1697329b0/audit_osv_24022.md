# [H] KVM: x86: smm: number of GPRs in the SMRAM image depends on the image format

## Summary
Severity: High
Advisory: CVE-2022-49883
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49883
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.0.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: x86: smm: number of GPRs in the SMRAM image depends on the image format

On 64 bit host, if the guest doesn't have X86_FEATURE_LM, KVM will
access 16 gprs to 32-bit smram image, causing out-ouf-bound ram
access.

On 32 bit host, the rsm_load_state_64/enter_smm_save_state_64
is compiled out, thus access overflow can't happen.

## References
- https://git.kernel.org/stable/c/696db303e54f7352623d9f640e6c51d8fa9d5588
- https://git.kernel.org/stable/c/a7ebfbea0f52550d7cdf12c38f3f5eaa7b2b6494
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49883.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49883
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
