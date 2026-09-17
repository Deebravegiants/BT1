# [H] scsi: target: target_core_configfs: Add length check to avoid buffer overflow

## Summary
Severity: High
Advisory: CVE-2025-39998
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-10-15
Source: https://osv.dev/vulnerability/CVE-2025-39998
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.38 <5.4.301, >=5.5.0 <5.10.246, >=5.11.0 <5.15.195, >=5.16.0 <6.1.156, >=6.2.0 <6.6.110, >=6.7.0 <6.12.51, >=6.13.0 <6.16.11, >=6.17.0 <6.17.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: target: target_core_configfs: Add length check to avoid buffer overflow

A buffer overflow arises from the usage of snprintf to write into the
buffer "buf" in target_lu_gp_members_show function located in
/drivers/target/target_core_configfs.c. This buffer is allocated with
size LU_GROUP_NAME_BUF (256 bytes).

snprintf(...) formats multiple strings into buf with the HBA name
(hba->hba_group.cg_item), a slash character, a devicename (dev->
dev_group.cg_item) and a newline character, the total formatted string
length may exceed the buffer size of 256 bytes.

Since snprintf() returns the total number of bytes that would have been
written (the length of %s/%sn ), this value may exceed the buffer length
(256 bytes) passed to memcpy(), this will ultimately cause function
memcpy reporting a buffer overflow error.

An additional check of the return value of snprintf() can avoid this
buffer overflow.

## References
- https://git.kernel.org/stable/c/27e06650a5eafe832a90fd2604f0c5e920857fae
- https://git.kernel.org/stable/c/4b292286949588bd2818e66ff102db278de8dd26
- https://git.kernel.org/stable/c/53c6351597e6a17ec6619f6f060d54128cb9a187
- https://git.kernel.org/stable/c/764a91e2fc9639e07aac93bc70e387e6b1e33084
- https://git.kernel.org/stable/c/a150275831b765b0f1de8b8ff52ec5c6933ac15d
- https://git.kernel.org/stable/c/ddc79fba132b807ff775467acceaf48b456e008b
- https://git.kernel.org/stable/c/e6eeee5dc0d9221ff96d1b229b1d0222c8871b84
- https://git.kernel.org/stable/c/e73fe0eefac3e15bf88fb5b4afae4c76215ee4d4
- https://git.kernel.org/stable/c/f03aa5e39da7d045615b3951d2a6ca1d7132f881
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39998.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39998
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
