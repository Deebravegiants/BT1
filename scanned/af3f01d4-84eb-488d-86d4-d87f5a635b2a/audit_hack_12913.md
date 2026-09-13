# [M] It is possible to execute `Vault.open_position()` using a removed `token` from the whitelist

## Summary
Severity: Medium
Reporter: 0xbepresent
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1489
Type: audit-issue

## Details
# It is possible to execute `Vault.open_position()` using a removed `token` from the whitelist

## Summary

If a token is removed from the whitelist using the `Vault.remove_token_from_whitelist()` function, that token can be used by the `Vault.open_position()` to open a trade. That behaivour is incorrect because the removed token from the whitelist should not be able as a valid token in the new open positions. 

## Vulnerability Detail

The [Vault.whitelist_token()](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1489) function helps to add a token to [the whitelist](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1482). In the other hand, the [Vault.remove_token_from_whitelist()](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1489C5-L1489C32) function helps to remove the token from [the whitelist](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1493). Additionally the [Vault.enable_market()](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1497C5-L1497C18) helps to enable an specific [pair of tokens](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1500), so if one token from the pair [is not whitelisted](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1499), the market can not be enabled, that validation is in the 1499 code line.

```python
File: Vault.vy
1496: @external
1497: def enable_market(_token1: address, _token2: address, _max_leverage: uint256):
1498:     assert msg.sender == self.admin, "unauthorized"
1499:     assert (self.is_whitelisted_token[_token1] and self.is_whitelisted_token[_token2]), "invalid token"
1500:     self.is_enabled_market[_token1][_token2] = True
1501:     self.max_leverage[_token1][_token2] = _max_leverage
```

The problem here is that if a `token` is removed from the whitelist using the `Vault.remove_token_from_whitelist` function, the markets that are using that `token` are not disabled for future open positions. As you can see in the [173 code line](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L173), the validation if a token is enabled is using the `enabled_market` array:

```python
File: Vault.vy
155: @nonreentrant("lock")
156: @external
157: def open_position(
158:     _account: address,
159:     _position_token: address,
160:     _min_position_amount_out: uint256,
161:     _debt_token: address,
162:     _debt_amount: uint256,
163:     _margin_amount: uint256,
164: ) -> (bytes32, uint256):
...
...
173:     assert self.is_enabled_market[_debt_token][_position_token], "market not enabled"
...
...
```

So, traders can open positions using a token that is removed from the whitelist. I created the next test where the token `USDC` is removed from the whitelist and it is possible to open a position using the `USDC` token. Test steps:

1. Assert `USDC` is whitelisted token
2. Remove `USDC` from the whitelist token
3. It is possible to open position even when the `USDC` is not a whitelisted token

```python
# File: test_whitelisttoken.py
# $ pytest -k "test_whitelisttoken_removetokenfromwhitelist"
import pytest
import boa

BASE_LP = False


@pytest.fixture(autouse=True)
def setup(vault, mock_router, owner, usdc, weth):
    vault.set_swap_router(mock_router.address)
    vault.set_is_whitelisted_dex(owner, True)
    usdc.approve(vault.address, 999999999999999999)
    vault.fund_account(usdc.address, 1000000000)
    vault.provide_liquidity(usdc, 1000000000000, BASE_LP)


def test_whitelisttoken_removetokenfromwhitelist(vault, owner, weth, usdc):
    """
    Test the remove_token_from_whitelist() does not disable the market so it is possible
    open trades with that removed token from the whitelist.

    1. Assert USDC is whitelisted token
    2. Remove USDC from the whitelist token
    3. It is possible to open position even when the USDC is not a whitelisted token
    """
    #
    # Assert USDC is whitelisted token
    #
    assert vault.is_whitelisted_token(pytest.USDC) == True
    #
    # Remove USDC from the whitelist token
    #
    vault.remove_token_from_whitelist(pytest.USDC)
    assert vault.is_whitelisted_token(pytest.USDC) == False
    #
    # It is possible to open position even when the USDC is not a whitelisted token
    #
    uid, _ = vault.open_position(
        owner,  # account
        weth,  # position_token
        1 * 10**18,  # min_position_amount_out
        usdc,  # debt_token
        900 * 10**6,  # debt_amount
        111 * 10**6,  # margin_amount
    )
    position = vault.positions(uid)
    margin = position[3]
    assert margin == 111 * 10**6
```

## Impact

It is possible to open positions using a token removed from the whitelist. There are many reasons to remove a token from the whitelist, so new trades should not be able to use removed tokens.

## Code Snippet

The [Vault.open_position()](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L157) function

The [Vault.whitelist_token()](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1478), [Vault.remove_token_from_whitelist()](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1489) and [Vault.enable_market()](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1497C1-L1501C56) functions:

```python
File: Vault.vy
1477: @external
1478: def whitelist_token(_token: address, _token_to_usd_oracle: address) -> uint256:
1479:     assert msg.sender == self.admin, "unauthorized"
1480:     assert self.is_whitelisted_token[_token] == False, "already whitelisted"
1481: 
1482:     self.is_whitelisted_token[_token] = True
1483:     self.to_usd_oracle[_token] = _token_to_usd_oracle
1484: 
1485:     return self._to_usd_oracle_price(_token)
1486: 
1487: 
1488: @external
1489: def remove_token_from_whitelist(_token: address):
1490:     assert msg.sender == self.admin, "unauthorized"
1491:     assert self.is_whitelisted_token[_token] == True, "not whitelisted"
1492:     self.to_usd_oracle[_token] = empty(address)
1493:     self.is_whitelisted_token[_token] = False
1494: 
1495: 
1496: @external
1497: def enable_market(_token1: address, _token2: address, _max_leverage: uint256):
1498:     assert msg.sender == self.admin, "unauthorized"
1499:     assert (self.is_whitelisted_token[_token1] and self.is_whitelisted_token[_token2]), "invalid token"
1500:     self.is_enabled_market[_token1][_token2] = True
1501:     self.max_leverage[_token1][_token2] = _max_leverage
```


## Tool used

Manual review

## Recommendation

The market is enabled if [both tokens are whitelisted](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1499) and the [max leverage is configured](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1501), so it could be possible to create an internal function which uses that validation and use the new function in the `Vault.open_position()` function.

```python
@internal
def _is_market_enabled(_token1: address, _token2: address):
    return (self.is_whitelisted_token[_token1] and self.is_whitelisted_token[_token2] and self.max_leverage[_token1][_token2] != 0)
```

```diff
def open_position(
    _account: address,
    _position_token: address,
    _min_position_amount_out: uint256,
    _debt_token: address,
    _debt_amount: uint256,
    _margin_amount: uint256,
) -> (bytes32, uint256):
    """
    @notice
        Creates a new undercollateralized loan for _account
        and uses it to assume a leveraged spot position in
        _position_token.
    """
    assert self.is_accepting_new_orders, "paused"
    assert self.is_whitelisted_dex[msg.sender], "unauthorized"
--  assert self.is_enabled_market[_debt_token][_position_token], "market not enabled"
++  assert self._is_market_enabled(_debt_token, _position_token), "market not enabled"
```
