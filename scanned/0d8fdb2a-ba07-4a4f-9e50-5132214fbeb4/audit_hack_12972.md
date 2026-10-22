# [H] An Attacker can Increase his `WETH` margin without actually depositing `ETH`

## Summary
Severity: High
Reporter: shealtielanz
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L767C1-L781C54
Type: audit-issue

## Details
# An Attacker can Increase his `WETH` margin without actually depositing `ETH`

## Summary
In the vault.vy allows the user to fund their `WETH` margin by depositing `ETH` through the `fund_account_eth()` function. However, the function is missing some checks that allow an attacker to gain `WETH` without actually depositing `ETH`.
## Vulnerability Detail
In the `fund_account_eth()` function the user's balance is increased by the `msg.value` sent during the execution of the function, and it calls the `WETH` contract's deposit function with an unchecked `low-level` call using the `msg.value` as the `call.value`      ------>
```vyper
@nonreentrant("lock")
@payable
@external
def fund_account_eth():
    """
    @notice
        Allows a user to fund his WETH margin by depositing ETH.
    """
    assert self.is_accepting_new_orders, "funding paused"
    assert self.is_whitelisted_token[WETH], "token not whitelisted"
    self.margin[msg.sender][WETH] += msg.value
    raw_call(WETH, method_id("deposit()"), value=msg.value)
    log AccountFunded(msg.sender, msg.value, WETH)
```
The issue here is, if the `low-level` call fails, it fails silently and the function doesn't revert but carries on its operation this is because there is no check on the return values of the `call`, which is dangerous ----> However an attacker can do one of these things.

- Force the call stack dept to reach `1024`, which will make the `low-level` call fail.
- Make the recipient address run out of `gas`.

if this happens successfully, the attacker receives his `msg.value` back because the call failed however due to that was ignored by the function, the attacker's balance of WETH margin is still increased by the `msg.value` sent and the attacker can withdraw more `ETH` for `WETH` he didn't actually deposit, so without the contract knowing this it uses its own balance to compensate the Attacker.

Same attack surface as the [`provide_liquidity_eth()`](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L767C1-L781C54) function. where it also does a `low-level` call that could fail silently, while believing the attacker actually deposited `ETH`.
## Impact
An attacker can increase their `WETH` margin without actually depositing `ETH`, which will can a significant loss of funds to the protocol. This Impact is critical as the surface of the attack is easy but the gain is massive for the attacker.
## Code Snippet
- The `fund_account_eth()` Function ~ [Click here](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L656C1-L668C51)
## Tool used

Manual Review

## Recommendation
Check the return values of the `low-level` call, and revert the whole transaction if the call fails.
