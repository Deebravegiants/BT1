# [M] CVE-2023-49100

## Summary
Severity: Medium
Advisory: CVE-2023-49100
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-21
Source: https://osv.dev/vulnerability/CVE-2023-49100
Type: osv

## Details
Trusted Firmware-A (TF-A) before 2.10 has a potential read out-of-bounds in the SDEI service. The input parameter passed in register x1 is not validated well enough in the function sdei_interrupt_bind. The parameter is passed to a call to plat_ic_get_interrupt_type. It can be any arbitrary value passing checks in the function plat_ic_is_sgi. A compromised Normal World (Linux kernel) can enable a root-privileged attacker to issue arbitrary SMC calls. Using this primitive, he can control the content of registers x0 through x6, which are used to send parameters to TF-A. Out-of-bounds addresses can be read in the context of TF-A (EL3). Because the read value is never returned to non-secure memory or in registers, no leak is possible. An attacker can still crash TF-A, however.

## References
- https://github.com/ARM-software/arm-trusted-firmware/blob/a05414bedc9b1cc35cf0795ce641b6b4db5bc97e/services/std_svc/sdei/sdei_main.c#L708
- https://github.com/ARM-software/arm-trusted-firmware/blob/a05414bedc9b1cc35cf0795ce641b6b4db5bc97e/services/std_svc/sdei/sdei_main.c#L714
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/49xxx/CVE-2023-49100.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-49100
- https://trustedfirmware-a.readthedocs.io/en/latest/security_advisories/security-advisory-tfv-11.html
