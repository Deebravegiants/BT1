# [H] FuelVM is vulnerable to heap memory allocation re-use bug

## Summary
Severity: High
Advisory: GHSA-2pgj-5cv2-6xxw
CWE: CWE-416
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-08
Source: https://github.com/advisories/GHSA-2pgj-5cv2-6xxw
Type: github-advisory

## Affected
- crates.io: `fuel-vm` — affected >=0 <0.59.3
- crates.io: `fuel-vm` — affected >=0.60.0 <0.60.1

## Details
### Impact

A memory safety vulnerability was present in the Fuel Virtual Machine (FuelVM), where memory reads could bypass expected access controls. Specifically, when a smart contract performed a `mload` (or other opcodes which access memory) on memory that had been deallocated using `ret`, it was still able to access the old memory contents. This occurred because the memory region was not zeroed out or otherwise marked as invalid. As a result, smart contracts could potentially read sensitive data left over from other contracts if the same memory was reallocated, violating isolation guarantees between contracts and enabling unintended data leakage.

All users running affected versions of FuelVM that relied on strict memory isolation between smart contracts were impacted.

### Patches

The vulnerability was patched by modifying the FuelVM to ensure that memory deallocated with `ret` was zeroed out or made inaccessible. The fix was included in FuelVM version `v0.60.1` and back-ported to `v0.59.3`. This patch was released to the Fuel network on Friday, April 18th, 2025.

### Workarounds

There were no reliable workarounds that fully mitigated the vulnerability. While developers could manually zero out sensitive memory regions before returning from a function, this approach was error-prone and could not be enforced at the VM level. Upgrading to a patched version remained the recommended course of action.

### References

- Fix implemented in the FuelVM GitHub repository (https://github.com/FuelLabs/fuel-vm/pull/941)

## References
- https://github.com/FuelLabs/fuel-vm/security/advisories/GHSA-2pgj-5cv2-6xxw
- https://github.com/FuelLabs/fuel-vm/pull/941
- https://github.com/FuelLabs/fuel-vm/commit/9c97c2bf782626b35ba48e154f210f91c847a513
- https://github.com/FuelLabs/fuel-vm
