# [M] ERC4626 inflat issue mitigation is not sufficient

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-01-opus
Published: 2024-02-06
Source: https://github.com/code-423n4/2024-01-opus-findings/issues/179
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-01-opus/blob/4720e9481a4fb20f4ab4140f9cc391a23ede3817/src/core/gate.cairo#L191-L223
https://github.com/code-423n4/2024-01-opus/blob/4720e9481a4fb20f4ab4140f9cc391a23ede3817/src/core/absorber.cairo#L667-L705


# Vulnerability details

## Impact
Both `absorber` and `gate` use the same mitigation for ERC4626 first depositor front-running vulnerability, but current implementation is not sufficient. By abusing the flaw, even though malicious attacker can't benefit from the mitigation, he can cause other normal users lose asset.

## Proof of Concept
Because of `absorber` and `gate` use the same mitigation, I will take `gate` as example.

Suppose the yang's decimals is **18**

When [sentinel.add_yang](https://github.com/code-423n4/2024-01-opus/blob/4720e9481a4fb20f4ab4140f9cc391a23ede3817/src/core/sentinel.cairo#L174-L214) is called to add yang to shrine, `initial_yang_amt` is passed to [shrine.add_yang](https://github.com/code-423n4/2024-01-opus/blob/4720e9481a4fb20f4ab4140f9cc391a23ede3817/src/core/sentinel.cairo#L209) as mitigation to the inflat issue.
And [initial_yang_amt](https://github.com/code-423n4/2024-01-opus/blob/4720e9481a4fb20f4ab4140f9cc391a23ede3817/src/core/sentinel.cairo#L202) is set as [INITIAL_DEPOSIT_AMT](https://github.com/code-423n4/2024-01-opus/blob/4720e9481a4fb20f4ab4140f9cc391a23ede3817/src/core/sentinel.cairo#L33) which is `const INITIAL_DEPOSIT_AMT: u128 = 1000;`

In [sentinel.cairo#L204-L206](https://github.com/code-423n4/2024-01-opus/blob/4720e9481a4fb20f4ab4140f9cc391a23ede3817/src/core/sentinel.cairo#L204-L206), `yang_erc20.transfer_from` is called to transfer 1000 wei yang_erc from caller to gate

And then the code flow will fall into [shrine.add_yang](https://github.com/code-423n4/2024-01-opus/blob/4720e9481a4fb20f4ab4140f9cc391a23ede3817/src/core/shrine.cairo#L565-L618), when the function is called, `initial_yang_amt` is still `1000`

In `shrine.add_yang`, the `yang_total` will be set to `1000` in [shrine.cairo#L591](https://github.com/code-423n4/2024-01-opus/blob/4720e9481a4fb20f4ab4140f9cc391a23ede3817/src/core/shrine.cairo#L591)

So when the admin(which is the first depositor) calls [sentinel.add_yang](https://github.com/code-423n4/2024-01-opus/blob/4720e9481a4fb20f4ab4140f9cc391a23ede3817/src/core/sentinel.cairo#L174-L214), he will transfer 1000 wei yang_asset and he will recevie 1000 yang_amt yang.
After that, when the second user calls [abbot.open_trove](https://github.com/code-423n4/2024-01-opus/blob/4720e9481a4fb20f4ab4140f9cc391a23ede3817/src/core/abbot.cairo#L131-L161), [gate.convert_to_yang_helper](https://github.com/code-423n4/2024-01-opus/blob/4720e9481a4fb20f4ab4140f9cc391a23ede3817/src/core/gate.cairo#L208-L222) will calculate his `yang_amt` by [gate.cairo#L220](https://github.com/code-423n4/2024-01-opus/blob/4720e9481a4fb20f4ab4140f9cc391a23ede3817/src/core/gate.cairo#L220)
```rust
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
                (asset_amt.into() * total_yang) / get_total_assets_helper(asset).into() <<<--- the second user calcuates the `yang_amout` using this code
            }
        }
```
And [gate.get_total_assets_helper](https://github.com/code-423n4/2024-01-opus/blob/4720e9481a4fb20f4ab4140f9cc391a23ede3817/src/core/gate.cairo#L230-L232) is using `asset.balance_of`.
```rust
    #[inline(always)]
    fn get_total_assets_helper(asset: IERC20Dispatcher) -> u128 {
        asset.balance_of(get_contract_address()).try_into().unwrap() <<<--- balance_of is used here
    }
```

So to sum up, in current implementation:
1) the first depositor(which is also the admin) will depost 1000 wei ERC, and will receive 1000 yang_amt
2) the second depostor will get his yang_amt based of [(asset_amt.into() * total_yang) / get_total_assets_helper(asset).into()](https://github.com/code-423n4/2024-01-opus/blob/4720e9481a4fb20f4ab4140f9cc391a23ede3817/src/core/gate.cairo#L220C17-L220C88)

Suppose in a case that the asset is DAI(18 decimals)
1) when yang_dai is created, the admin calls add_yang to add DAI into the protocol, and he will transfer 1000 wei DAI to `gate`, and will receive 1000 yang_amt
2) a malicious tranfers (100000 * 1e18 - 1000 wei) DAI(which is worth 100000 USD) to `gate`
3) Alice a normal user deposit 199* 1e18 DAI(which is worth 199 USD) by calling [abbot.open_trove](https://github.com/code-423n4/2024-01-opus/blob/4720e9481a4fb20f4ab4140f9cc391a23ede3817/src/core/abbot.cairo#L131-L161), based on [gate.cairo#L220](https://github.com/code-423n4/2024-01-opus/blob/4720e9481a4fb20f4ab4140f9cc391a23ede3817/src/core/gate.cairo#L220), Alice will get 199 * 1e18 * 1000 / (100000 * 1e18) = 1 wei
4) If Alice wants to close her trove, [gate.convert_to_assets](https://github.com/code-423n4/2024-01-opus/blob/4720e9481a4fb20f4ab4140f9cc391a23ede3817/src/core/gate.cairo#L126-L128) will be used to calculate the asset amount, according to [gate.cairo#L191-L204](https://github.com/code-423n4/2024-01-opus/blob/4720e9481a4fb20f4ab4140f9cc391a23ede3817/src/core/gate.cairo#L191-L204), [gate.cairo#L202](https://github.com/code-423n4/2024-01-opus/blob/4720e9481a4fb20f4ab4140f9cc391a23ede3817/src/core/gate.cairo#L202) will be used: `((yang_amt * get_total_assets_helper(asset).into()) / total_yang).val`, because alice has 1 wei yang_amout, and `get_total_assets_helper()` is __(100000 + 199) * 1e18__, `total_yang` will be 1001
So Alice will get __1 * (100000 * 1e18 + 199*1e18) / (1000 + 1)__ = 100.0989010989011 * 1e18, which is 100 USD. And the remaining 99*1e18 DAI will be in the gate.

In the above case, there will be two issue:
1. Alice will lose her asset
1. After Alice's close her trove, the system's balance will be (100000 + 99)*1e18, which is becoming larger. And the balance will keep growing with time going, which will cause users losing more asset.



## Tools Used
VIM

## Recommended Mitigation Steps
In [gate.get_total_assets_helper](https://github.com/code-423n4/2024-01-opus/blob/4720e9481a4fb20f4ab4140f9cc391a23ede3817/src/core/gate.cairo#L230C8-L232), don't use balance_of to calculate the amount, instead, define a new variables and record the deposited asset amount by the variables



## Assessed type

ERC4626
