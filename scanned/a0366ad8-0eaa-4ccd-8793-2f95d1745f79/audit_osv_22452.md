# [H] CVE-2022-2962

## Summary
Severity: High
Advisory: CVE-2022-2962
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-09-13
Source: https://osv.dev/vulnerability/CVE-2022-2962
Type: osv

## Details
A DMA reentrancy issue was found in the Tulip device emulation in QEMU. When Tulip reads or writes to the rx/tx descriptor or copies the rx/tx frame, it doesn't check whether the destination address is its own MMIO address. This can cause the device to trigger MMIO handlers multiple times, possibly leading to a stack or heap overflow. A malicious guest could use this flaw to crash the QEMU process on the host, resulting in a denial of service condition.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/2xxx/CVE-2022-2962.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-2962
- https://gitlab.com/qemu-project/qemu/-/issues/1171
- https://gitlab.com/qemu-project/qemu/-/commit/36a894aeb64a2e02871016da1c37d4a4ca109182
