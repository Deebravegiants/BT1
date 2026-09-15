# [M] YieldCore incident: The YieldCore-3rd-deal vault under Trading Protocol was exploited. The attacker took advantage of a missing caller authorization c

## Summary
Severity: Medium
Target: YieldCore
Loss: $ 398,000
Attack method: Smart Contract Vulnerability
Published: 2026-04-28
Source: https://x.com/DefimonAlerts/status/2049365873069097237
Type: slowmist-incident

## Details
The YieldCore-3rd-deal vault under Trading Protocol was exploited. The attacker took advantage of a missing caller authorization check in the contract, bypassing the permission mechanism and draining all funds from the vault in one go. The vault was permissionlessly listed (not a core part of the protocol itself). The entire vault was emptied.
