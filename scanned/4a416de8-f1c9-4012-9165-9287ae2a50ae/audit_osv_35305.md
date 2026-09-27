# [H] CVE-2025-70956

## Summary
Severity: High
Advisory: CVE-2025-70956
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-02-13
Source: https://osv.dev/vulnerability/CVE-2025-70956
Type: osv

## Details
A State Pollution vulnerability was discovered in the TON Virtual Machine (TVM) before v2025.04. The issue exists in the RUNVM instruction logic (VmState::run_child_vm), which is responsible for initializing child virtual machines. The operation moves critical resources (specifically libraries and log) from the parent state to a new child state in a non-atomic manner. If an Out-of-Gas (OOG) exception occurs after resources are moved but before the state transition is finalized, the parent VM retains a corrupted state where these resources are emptied/invalid. Because RUNVM supports gas isolation, the parent VM continues execution with this corrupted state, leading to unexpected behavior or denial of service within the contract's context.

## References
- https://gist.github.com/Lucian-code233/beab9d14683ed2bdf5543be430b91c70
- https://github.com/ton-blockchain/ton/releases/tag/v2025.04#:~:text=Arayz%2C%20Robinlzw%2C%20%40wy666444%20%40Lucian-code233
- https://mp.weixin.qq.com/s/ZD35baKUikefFdtNHZIC9g
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/70xxx/CVE-2025-70956.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-70956
- https://github.com/ton-blockchain/ton/commit/1835d84602bbaaa1593270d7ab3bb0b499920416
