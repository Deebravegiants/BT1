# [H] convert_to_yang_helper() loss precision

## Summary
Severity: High
Chain: Smart contract
Component: 2024-01-opus
Published: 2024-02-06
Source: https://github.com/code-423n4/2024-01-opus-findings/issues/195
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-01-opus/blob/4720e9481a4fb20f4ab4140f9cc391a23ede3817/src/core/gate.cairo#L220


# Vulnerability details

## Vulnerability details
in `gate.cairo`
When the user calls `deposit()`, it calculates the corresponding shares through `convert_to_yang_helper()`. 
The code is as follows:
```cairo
        fn convert_to_yang_helper(self: @ContractState, asset_amt: u128) -> Wad {
            let asset: IERC20Dispatcher = self.asset.read();
            let total_yang: Wad = self.get_total_yang_helper(asset.contract_address);

            if total_yang.is_zero() {
                let decimals: u8 = asset.decimals();
                // Otherwise, scale `asset_amt` up by the difference to match `Wad`
                // precision of yang. If asset is of `Wad` precision, then the same
                // value is returned
                fixed_point_to_wad(asset_amt, decimals)
            } else {
@>              (asset_amt.into() * total_yang) / get_total_assets_helper(asset).into()
            }
        }
```
The calculation formula is: `(asset_amt.into() * total_yang) / get_total_assets_helper(asset).into()`

The actual calculation of converting Wad to pure numbers is: `(asset_amt * total_yang / 1e18) * 1e18 / total_assets`

The above formula `(asset_amt * total_yang / 1e18)` will lose precision, especially when the asset's decimals are less than 18.

Assume btc as an example, decimals = 8
after `add_yang(btc)` INITIAL_DEPOSIT_AMT = 1000 so: 
total_assets = 1000
total_yang   = 1000e10 = 1e13


_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-01-opus-findings/issues/195_
