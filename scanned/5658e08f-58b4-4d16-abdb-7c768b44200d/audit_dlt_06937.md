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

If the user deposits 0.0009e8 BTC, according to the formula
= (asset_amt * total_yang / 1e18) 
=  0.0009e8 * 1e13 /1e18 = 0.9e5 * 1e13 /1e18 =  0

With BTC's price at 40,000 USD, 0.0009e8  =  36 USD

The user will lose 36 USD

We should cancel dividing by 1e18 and then multiplying by 1e18, and calculate directly
shares = `asset_amt.into() * total_yang.into() / total_assets.into()`
shares = 0.0009e8 * 1e13 / 1000 = 0.0009e18 = 900000000000000


> Note: In order to successfully deposit should be > 0.0009e8 such as 0.0019e8, which is simplified and convenient to explain.
## Impact

Due to the premature division by `1e18`, precision is lost, and the user loses a portion of their funds.

## Proof of Concept
add to test_abbot.cairo
```cairo
    #[test]
    fn test_wad() {
        let INITIAL_DEPOSIT_AMT: u128 = 1000;
        let decimals:u8 = 8;
        let asset_amt:u128 = 90_000;
        let total_yang:Wad = fixed_point_to_wad(INITIAL_DEPOSIT_AMT, decimals);
        let total_assets:Wad = INITIAL_DEPOSIT_AMT.into();
        let result:Wad = asset_amt.into() * total_yang / total_assets;
        assert(result.into() == 0,' no zero');
        let result2_u:u256 = asset_amt.into() * total_yang.into() / total_assets.into();
        let result2:Wad = Wad { val:result2_u.try_into().expect('u128')};
        assert(result2.into() == 900000000000000,' result2 no zero');
    }
```

```console
$ scarb test -vvv test_wad 

Running 1 test(s) from src/
[PASS] opus::tests::abbot::test_abbot::test_abbot::test_wad (gas: ~17)
Tests: 1 passed, 0 failed, 0 skipped, 0 ignored, 390 filtered out

```

## Recommended Mitigation
```diff
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
-               (asset_amt.into() * total_yang) / get_total_assets_helper(asset).into()
+               let result:u256 = asset_amt.into() * total_yang.into() / total_assets.into();
+               Wad { val:result.try_into().expect('u128')};
            }
        }
```


## Assessed type

Decimal
