# [H] reduce_margin_by_amountin Vault.reduce_position

## Summary
Severity: High
Contest weight: 0.6579
Dataset id: 20181
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In Vault.reduce_position, some position tokens are sold and debt and margin are reduced. The remaining amount of debt and margin should maintain the same leverage as before. However, the reduced amount is wrongly calculated and as a result, the leverage is changed. Suppose that the debt amount is 9000 USDC and the margin amount is also 9000 USDC. And the amount_out_received is 9000 USDC. Let’s take a look of the calculation: We can find out that the reduced amount of margin is 9000 and the reduced amount of debt is 0. The leverage is changed. I also wrote a test to demonstrate the issue. (The test case is different from the previous case)
def test_reduce_position(vault, owner, weth, usdc, mock_router, eth_usd_oracle):
    eth_usd_oracle.set_answer(9000_00000000)
    assert vault.swap_router() == mock_router.address
    uid, amount_bought = vault.open_position(
        owner,
        # account
        weth,
        # position_token
        2 * 10**18,
        # min_position_amount_out
        usdc,
        # debt_token
        9000 * 10**6,
        # debt_amount
        9000 * 10**6,
        # margin_amount
    )
    position_before = vault.positions(uid)
    position_amount_before = position_before[6]
    assert position_amount_before == 2 * 10**18
    margin_amount_before = position_before[3]
    assert margin_amount_before == 9000 * 10**6
    debt_amount_before = vault.debt(uid)
    assert debt_amount_before == 9000 * 10**6
    vault.reduce_position(uid, int(position_amount_before/3), 6000 * 10**6)
    position_after = vault.positions(uid)
    debt_amount_after = vault.debt_shares_to_amount(usdc.address, position_after[4])
    print(debt_amount_after)
    assert debt_amount_after == pytest.approx(6000 * 10**6, abs=10000000) # is 9000 * 10**6
    margin_amount_after = position_after[3]
    print(margin_amount_after)
    assert margin_amount_after == pytest.approx(6000 * 10**6, abs=1000000)
    position_amount_after = position_after[6]
Besides, I want to mention that the usage of pytest.approx is incorrect in assert debt_amount_after == pytest.approx(6000 * 10**6, 10000000). If the approximation means 6000 * 10 ** 6 ± 10000000, it should be pytest.approx(6000 * 10**6, abs=10000000). On the other hand, pytest.approx(6000 * 10**6, 10000000) considers numbers within a relative tolerance of the expected value. The approximation 6000 * 10 ** 6 ± (6000 * 10**6 * 10000000) has too large of a range of values. The reduced amounts of debt and margin are wrongly calculated. The leverage is changed after reduce_position.

## Recommendation
```solidity
def reduce_position(
    _position_uid: bytes32, _reduce_by_amount: uint256, _min_amount_out: uint256
) -> uint256:
    ...
    margin_debt_ratio: uint256 = position.margin_amount * PRECISION / (
        debt_amount + position.margin_amount
    )
    amount_out_received: uint256 = self._swap(
        position.position_token, position.debt_token, _reduce_by_amount,
        min_amount_out
    )
    # reduce margin and debt, keep leverage as before
    reduce_margin_by_amount: uint256 = (
        amount_out_received * margin_debt_ratio / PRECISION
    )
    reduce_debt_by_amount: uint256 = amount_out_received - reduce_margin_by_amount
    position.margin_amount -= reduce_margin_by_amount
    burnt_debt_shares: uint256 = self._repay(position.debt_token, reduce_debt_by_amount)
    position.debt_shares -= burnt_debt_shares
    position.position_amount -= _reduce_by_amount
    self.positions[_position_uid] = position
    log PositionReduced(position.account, _position_uid, position, amount_out_received)
    return amount_out_received
```
