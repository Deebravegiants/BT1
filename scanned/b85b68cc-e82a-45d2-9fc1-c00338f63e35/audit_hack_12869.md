# [H] MarginDex.open_trade() allows bad actors to drain all debt tokens

## Summary
Severity: High
Reporter: whiteh4t9527
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L182
Type: audit-issue

## Details
# MarginDex.open_trade() allows bad actors to drain all debt tokens

## Summary
By providing some margin, a bad actor could swap debt tokens to position tokens by opening a position with `open_trade()`. However, the underlying `Vault.open_position()` fails to check if the *debt-to-position* swap is within a reasonable price range, leading to possible attacks to drain all debt tokens.

## Vulnerability Detail
In `Vault.open_position()`, a whitelisted dex (e.g., MarginDex) can open a position with `_margin_amount` of debt token and leverage `_debt_token` of debt token. Later on, `_margin_amount + _debt_token` of debt tokens would be exchanged to position tokens. However, the [swap operation](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L182) fails to check the slippage (i.e., `_min_position_amount_out`) such that a bad actor could intentionally provide enough margin, leverage all debt tokens, and exchange them to position token with unlimited slippage (i.e., `_min_position_amount_out = 0`). By creating an UniswapV3 position in advance, those debt tokens would be exchanged to a tiny amount of position token (e.g., 1 wei of ETH) and the attacker can walk away with all debt tokens. 

## Impact
Bad actors can drain all debt tokens

## Code Snippet
```vyper
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
    assert self.is_enabled_market[_debt_token][_position_token], "market not enabled"
    assert self.margin[_account][_debt_token] >= _margin_amount, "not enough margin"
    assert ((_debt_amount + _margin_amount) * PRECISION / _margin_amount) <= self.max_leverage[_debt_token][_position_token] * PRECISION, "too much leverage"
    assert (self._available_liquidity(_debt_token) >= _debt_amount), "insufficient liquidity"

    self.margin[_account][_debt_token] -= _margin_amount
    debt_shares: uint256 = self._borrow(_debt_token, _debt_amount)

    token_in_amount: uint256 = _debt_amount + _margin_amount
    amount_bought: uint256 = self._swap(
        _debt_token, _position_token, token_in_amount, _min_position_amount_out
    )
```

## Tool used

Manual Review

## Recommendation
Check if the position is liquidatable before opening it
