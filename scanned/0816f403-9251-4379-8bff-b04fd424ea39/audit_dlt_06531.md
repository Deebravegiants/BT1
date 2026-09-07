# [M] plain `approve` will impact `DepositBatch` for USDT token when multi-chain deployment active

## Summary
Severity: Medium
Chain: Smart contract
Component: Velvet-Capital
Published: 2024-06-20
Source: https://github.com/hats-finance/Velvet-Capital-0x0bb0c08fd9eeaf190064f4c66f11d18182961f77/issues/3
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x3b176f1644b312569f5ab491f6c1d4101a3dad77de404565732eeac32fdb36ca
**Severity:** medium

**Description:**
**Description:**

In `DepositBatch`, `multiTokenSwapAndTransfer` function, there is a plain `Approve` ERC20 function which need to be concerned.

When the `_token` being approved is USDT in Mainnet, it's a well-known issue it will be reverted. The token have limitations when it comes to modifying the allowance from a non-zero value. For instance, the approve() function of Tether (USDT) will throw an error if the current approval is not set to zero.

Based on velvet capital docs, with current depoloyment (BSC and Arbitrum) this USDT is not being an issue, but the `Intent OS` is aim for multi-chain deployment. 

```js
File: DepositBatch.sol
28:   function multiTokenSwapAndTransfer(
29:     FunctionParameters.BatchHandler memory data
30:   ) external payable nonReentrant{
...
50:     // Perform swaps and calculate deposit amounts for each token
51:     for (uint256 i; i < tokenLength; i++) {
52:       address _token = tokens[i];
53:       uint256 balance;
54:       if (_token == _depositToken) {
55:         //Sending encoded balance instead of swap calldata
56:         balance = abi.decode(data._callData[i], (uint256));
57:       } else {
58:         (bool success, ) = SWAP_TARGET.delegatecall(data._callData[i]);
59:         if (!success) revert ErrorLibrary.CallFailed();
60:         balance = _getTokenBalance(_token, address(this));
61:       }
62:       if (balance == 0) revert ErrorLibrary.InvalidBalanceDiff();
63: @>    IERC20(_token).approve(data._target, balance);
64:       depositAmounts[i] = balance;
65:     }
```


_Trimmed to 38 lines — full report: https://github.com/hats-finance/Velvet-Capital-0x0bb0c08fd9eeaf190064f4c66f11d18182961f77/issues/3_
