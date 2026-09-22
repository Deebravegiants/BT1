# [M] tpm: tpm_crb: Add the missed acpi_put_table() to fix memory leak

## Summary
Severity: Medium
Advisory: CVE-2022-50389
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2022-50389
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.0.0 <4.14.303, >=4.15.0 <4.19.270, >=4.20.0 <5.4.229, >=5.5.0 <5.10.163, >=5.11.0 <5.15.87, >=5.16.0 <6.0.17, >=6.1.0 <6.1.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

tpm: tpm_crb: Add the missed acpi_put_table() to fix memory leak

In crb_acpi_add(), we get the TPM2 table to retrieve information
like start method, and then assign them to the priv data, so the
TPM2 table is not used after the init, should be freed, call
acpi_put_table() to fix the memory leak.

## References
- https://git.kernel.org/stable/c/08fd965521d0e172d540cf945517810895fcb199
- https://git.kernel.org/stable/c/0bd9b4be721c776f77adcaf34105dfca3007ddb9
- https://git.kernel.org/stable/c/1af2232b13837ce0f3a082b9f43735b09aafc367
- https://git.kernel.org/stable/c/2fcd3dc8b97a14f1672729c86b7041a1a89b052a
- https://git.kernel.org/stable/c/37e90c374dd11cf4919c51e847c6d6ced0abc555
- https://git.kernel.org/stable/c/927860dfa161ae8392a264197257dbdc52b26b0f
- https://git.kernel.org/stable/c/986cd9a9b95423e35a2cbb8e9105aec0e0d7f337
- https://git.kernel.org/stable/c/b0785edaf649e5f04dc7f75533e810f4c00e4106
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50389.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50389
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
