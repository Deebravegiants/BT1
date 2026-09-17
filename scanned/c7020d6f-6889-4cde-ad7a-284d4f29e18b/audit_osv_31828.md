# [M] ASoC: SOF: stream-ipc: Check for cstream nullity in sof_ipc_msg_data()

## Summary
Severity: Medium
Advisory: CVE-2025-21847
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-12
Source: https://osv.dev/vulnerability/CVE-2025-21847
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.6.80, >=6.7.0 <6.12.17, >=6.13.0 <6.13.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: SOF: stream-ipc: Check for cstream nullity in sof_ipc_msg_data()

The nullity of sps->cstream should be checked similarly as it is done in
sof_set_stream_data_offset() function.
Assuming that it is not NULL if sps->stream is NULL is incorrect and can
lead to NULL pointer dereference.

## References
- https://git.kernel.org/stable/c/2b3878baf90918a361a3dfd3513025100b1b40b6
- https://git.kernel.org/stable/c/62ab1ae5511c59b5f0bf550136ff321331adca9f
- https://git.kernel.org/stable/c/6c18f5eb2043ebf4674c08a9690218dc818a11ab
- https://git.kernel.org/stable/c/d8d99c3b5c485f339864aeaa29f76269cc0ea975
- https://git.kernel.org/stable/c/dfe25c554daa12ee26eb3540bbded57733ed5d9c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21847.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21847
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
