# [M] Solana Pay Vulnerable to Weakness in Transfer Validation Logic

## Summary
Severity: Medium
Chain: @solana/pay
Component: @solana/pay
CVE: CVE-2022-35917
CWE: Always-Incorrect Control Flow Implementation
Published: 2022-08-06
Source: https://github.com/advisories/GHSA-j47c-j42c-mwqq
Type: github-advisory

## Details
### Description
When a Solana Pay transaction is located using a [reference key](https://github.com/solana-labs/solana-pay/blob/master/SPEC.md#reference), it may be checked to represent a transfer of the desired amount to the recipient, using the supplied [`validateTransfer` function](https://github.com/solana-labs/solana-pay/blob/master/core/src/validateTransfer.ts). An edge case regarding this mechanism could cause the validation logic to validate multiple transfers.

### Impact
Most known Solana Pay point of sale applications are currently run on physical point of sale devices, which makes this issue unlikely to occur. However, there may be web-based point of sale applications using the protocol where it may be more likely to occur.

### Patches
This issue has been patched as of version [`0.2.1`](https://www.npmjs.com/package/@solana/pay/v/0.2.1). Users of the Solana Pay SDK should upgrade to it.
