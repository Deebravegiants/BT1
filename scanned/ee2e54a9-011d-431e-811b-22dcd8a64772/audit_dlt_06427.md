# [H] decrease in pocket_money_balance even if the transfer failed

## Summary
Severity: High
Chain: Smart contract
Component: Most--Aleph-Zero-Bridge
Published: 2024-03-19
Source: https://github.com/hats-finance/Most--Aleph-Zero-Bridge-0xab7c1d45ae21e7133574746b2985c58e0ae2e61d/issues/21
Type: hats-finding

## Details
**Github username:** @0xmahdirostami
**Twitter username:** 0xmahdirostami
**Submission hash (on-chain):** 0xd5bf26ded8721aae73504af9b0b8a4d0e1976659e20a492b2c94b902d229a3c4
**Severity:** high

**Description:**
**Description** 
In the `receive_request` function, there's a section of code where a transfer is attempted, and if it fails, it doesn't revert but still decrements `pocket_money_balance`.

``` 
                if data.pocket_money_balance >= data.pocket_money {
                    // don't revert if the transfer fails
                    _ = self
                        .env()
                        .transfer(dest_receiver_address.into(), data.pocket_money);
                    data.pocket_money_balance = data
                        .pocket_money_balance
                        .checked_sub(data.pocket_money)
                        .ok_or(MostError::Arithmetic)?;
                }
```

**Impact**  
This behavior is inconsistent and could lead to incorrect state management. If the transfer fails, the `pocket_money_balance` should not be decremented.
pocket_money_balance should remain same
