# [M] GebProxyActions incident: The GebProxyActions contract was exploited due to missing caller access control in the quitSystem function. Victims had previously

## Summary
Severity: Medium
Target: GebProxyActions
Loss: $ 14,000
Attack method: Smart Contract Vulnerability
Published: 2026-09-02
Source: https://x.com/SlowMist_Team/status/2094986310683705835
Type: slowmist-incident

## Details
The GebProxyActions contract was exploited due to missing caller access control in the quitSystem function. Victims had previously called it directly instead of via DSProxy delegatecall, setting ownsSAFE[safe] to the GebProxyActions contract. The attacker called GebProxyActions.quitSystem(manager, safe, dst) directly, bypassing GebSafeManager’s safeAllowed check and transferring collateral to themselves.
