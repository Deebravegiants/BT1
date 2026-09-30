# [?] fix(wallet): approval popup crash on network mismatch (#11058)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2026-04-01
Source: https://github.com/iotaledger/iota/commit/5cd22a1f64275610916cc7ecbc2e68ebe8d99572
Type: security-commit

## Details
fix(wallet): approval popup crash on network mismatch (#11058)

context
[here](https://github.com/iotaledger/iota/pull/10912#issuecomment-4153676538)

When the dashboard is on `testnet` and the wallet is on `devnet`, 
the transaction approval popup crashed because `useTransactionData` 
was trying to look up testnet objects on devnet — and those don't exist
there.

### Changes
- **Removed** `useTransactionData` from the approval flow — it was
redundant
  and caused the crash by ignoring the dapp's network (`chain` param)
- **Switched** to `useTransactionDryRun` — already supports the `chain`
parameter
  and provides the same loading/error states
- **Used** `transaction.getData()` for the details tab — no RPC call
needed,
  data is already available in the transaction object

---------

Co-authored-by: Bran <52735957+brancoder@users.noreply.github.com>
