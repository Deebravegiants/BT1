# [H] wifi: ath11k: Fix qmi_msg_handler data structure initialization

## Summary
Severity: High
Advisory: CVE-2022-50871
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-30
Source: https://osv.dev/vulnerability/CVE-2022-50871
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <6.0.16, >=6.1.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: ath11k: Fix qmi_msg_handler data structure initialization

qmi_msg_handler is required to be null terminated by QMI module.
There might be a case where a handler for a msg id is not present in the
handlers array which can lead to infinite loop while searching the handler
and therefore out of bound access in qmi_invoke_handler().
Hence update the initialization in qmi_msg_handler data structure.

Tested-on: IPQ8074 hw2.0 AHB WLAN.HK.2.5.0.1-01100-QCAHKSWPL_SILICONZ-1

## References
- https://git.kernel.org/stable/c/a10e1530c424bb277b4edc7def0195857a548495
- https://git.kernel.org/stable/c/d5d71de448f36e34592f7c81b5e300d3e8dbb735
- https://git.kernel.org/stable/c/ed3725e15a154ebebf44e0c34806c57525483f92
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50871.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50871
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
