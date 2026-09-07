# [M] after shut,  no pull redistribution yang will be locked

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-01-opus
Published: 2024-02-06
Source: https://github.com/code-423n4/2024-01-opus-findings/issues/202
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-01-opus/blob/4720e9481a4fb20f4ab4140f9cc391a23ede3817/src/core/caretaker.cairo#L288


# Vulnerability details

## Vulnerability details

in `caretaker.release()`
We can release the remaining yang.
```rust
        fn release(ref self: ContractState, trove_id: u64) -> Span<AssetBalance> {
            let shrine: IShrineDispatcher = self.shrine.read();
...
            loop {
                match yangs_copy.pop_front() {
                    Option::Some(yang) => {
@>                      let deposited_yang: Wad = shrine.get_deposit(*yang, trove_id);
                        let asset_amt: u128 = if deposited_yang.is_zero() {
                            0
                        } else {
                            let exit_amt: u128 = sentinel.exit(*yang, trove_owner, trove_id, deposited_yang);
                            // Seize the collateral only after assets have been
                            // transferred so that the asset amount per yang in Gate
                            // does not change and user receives the correct amount
                            shrine.seize(*yang, trove_id, deposited_yang);
                            exit_amt
                        };
                        released_assets.append(AssetBalance { address: *yang, amount: asset_amt });
                    },
                    Option::None => { break; },
                };
            };
```
As above, we can only release the yang that already exists in the trove: `shrine.get_deposit(*yang, trove_id);`

When `shire.get_live() == false`, we can no longer perform `shire.pull_redistributed_debt_and_yangs()`.

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-01-opus-findings/issues/202_
