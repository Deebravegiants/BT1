# [?] fix(state-viewer): fix balance overflow in state-dump command (#9546)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2023-10-02
Source: https://github.com/near/nearcore/commit/bfbea1878f0d0388182b1c733c51594f005a5d9d
Type: security-commit

## Details
fix(state-viewer): fix balance overflow in state-dump command (#9546)

The state-dump command changes the amounts of validator accounts to
match the epoch we're dumping state in, in case a validator stakes
during that epoch, and the locked amount is different than the stake.
The new locked amount computation is correct if a validator staked more,
but overflows if the locked amount is smaller than the stake plus
amount, which actually does occur on mainnet

## Patch
### tools/state-viewer/src/state_dump.rs
```diff
@@ -244,12 +244,14 @@ fn iterate_over_records(
                     continue;
                 }
                 if let StateRecord::Account { account_id, account } = &mut sr {
-                    total_supply += account.amount() + account.locked();
                     if account.locked() > 0 {
                         let stake = *validators.get(account_id).map(|(_, s)| s).unwrap_or(&0);
-                        account.set_amount(account.amount() + account.locked() - stake);
+                        if account.locked() > stake {
+                            account.set_amount(account.amount() + account.locked() - stake);
+                        }
                         account.set_locked(stake);
                     }
+                    total_supply += account.amount() + account.locked();
                 }
                 change_state_record(&mut sr, change_config);
                 callback(sr);
```
