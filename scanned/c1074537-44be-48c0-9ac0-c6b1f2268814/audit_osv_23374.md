# [H] i2c: mlxbf: prevent stack overflow in mlxbf_i2c_smbus_start_transaction()

## Summary
Severity: High
Advisory: CVE-2022-48632
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-28
Source: https://osv.dev/vulnerability/CVE-2022-48632
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.10.146, >=5.11.0 <5.15.71, >=5.16.0 <5.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

i2c: mlxbf: prevent stack overflow in mlxbf_i2c_smbus_start_transaction()

memcpy() is called in a loop while 'operation->length' upper bound
is not checked and 'data_idx' also increments.

## References
- https://git.kernel.org/stable/c/3b5ab5fbe69ebbee5692c72b05071a43fc0655d8
- https://git.kernel.org/stable/c/48ee0a864d1af02eea98fc825cc230d61517a71e
- https://git.kernel.org/stable/c/dc2a0c587006f29b724069740c48654b9dcaebd2
- https://git.kernel.org/stable/c/de24aceb07d426b6f1c59f33889d6a964770547b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48632.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48632
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
