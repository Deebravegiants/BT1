# [M] msg.sender is not validated for ZeroExAdapter.phutureOnConsumeCallbackV1()

## Summary
Severity: Medium
Contest weight: 0.5830
Dataset id: 13566
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
ZeroExAdapter.phutureOnConsumeCallbackV1() does not check if msg.sender is a whitelisted address. As such, anyone can call phutureOnConsumeCallbackV1() to perform arbitrary calls from ZeroExAdapter to any address:
```solidity
(bool success,) = params.target.call{value: params.currencyIn.isNative() ? params.amountIn : 0}(params.data);
if (!success) revert SwapFailed();
```
Although ZeroExAdapter does not hold any funds and has no state, this is still very dangerous. An attacker can use phutureOnConsumeCallbackV1() to manipulate the state of external contracts for ZeroExAdapter.
For example, to DOS rebalancing, an attacker can grant infinite USDT allowance from ZeroExAdapter to the 0x Exchange Proxy. Afterwards, when phutureOnConsumeCallbackV1() is called during rebalancing to swap USDT to other tokens, it will revert.
This is because USDT does not allow non-zero to non-zero approvals:
```solidity
function approve(address _spender, uint _value) public onlyPayloadSize(2 * 32) {
    // To change the approve amount you first have to reduce the addresses`
    // allowance to zero by calling `approve(_spender, 0)` if it is not
    // already 0 to mitigate the race condition described here:
    // https://github.com/ethereum/EIPs/issues/20#issuecomment-263524729
    require(!((_value != 0) && (allowed[msg.sender][_spender] != 0)));
}
```
However, phutureOnConsumeCallbackV1() performs a non-zero approval before attempting a swap:
```solidity
params.currencyIn.approve(params.target, params.amountIn);
```
As such, this call will always revert, making ZeroExAdapter permanently unusable for USDT swaps.

## Recommendation
In phutureOnConsumeCallbackV1(), consider validating that msg.sender is the vault/index address:
```diff
function phutureOnConsumeCallbackV1(bytes calldata data) external {
+   if (msg.sender != vault) revert NotAuthorized();
    TradeParams memory params = abi.decode(data, (TradeParams));
```
