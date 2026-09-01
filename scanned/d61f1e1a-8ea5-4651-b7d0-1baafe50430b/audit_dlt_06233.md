# [M] Wrong validation in `LiquidityPool.withdraw()`

## Summary
Severity: Medium
Chain: Smart contract
Component: ether-fi
Published: 2023-11-07
Source: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/19
Type: hats-finding

## Details
**Github username:** @KupiaSecAdmin
**Submission hash (on-chain):** 0xe39fc94c15055957c3e3dc97a8fac51f743434e0994e6589016f641d78fc46d1
**Severity:** medium

**Description:**
**Description**\
In `LiquidityPool.withdraw()`, it burns the caller's eETH balance and transfers eth to `recipient`. But during the validation at L178, it checks if `eETH.balanceOf(msg.sender) < _amount` which is wrong. `eETH.balanceOf(msg.sender)` should be compared with `share(eETH amount)`, not `_amount(eth amount)`.

```solidity
File: dappContracts\src\LiquidityPool.sol
175:     function withdraw(address _recipient, uint256 _amount) external whenNotPaused returns (uint256) {
176:         uint256 share = sharesForWithdrawalAmount(_amount);
177:         require(msg.sender == address(withdrawRequestNFT) || msg.sender == address(membershipManager), "Incorrect Caller");
178:         if (totalValueInLp < _amount || (msg.sender == address(withdrawRequestNFT) && ethAmountLockedForWithdrawal < _amount) || eETH.balanceOf(msg.sender) < _amount) revert InsufficientLiquidity(); //@audit eETH.balanceOf(msg.sender) < share
179:         if (_amount > type(uint128).max || _amount == 0 || share == 0) revert InvalidAmount();
180: 
181:         totalValueInLp -= uint128(_amount);
182:         if (msg.sender == address(withdrawRequestNFT)) {
183:             ethAmountLockedForWithdrawal -= uint128(_amount);
184:         }
185: 
186:         eETH.burnShares(msg.sender, share);
187: 
188:         (bool sent, ) = _recipient.call{value: _amount}("");
189:         if (!sent) revert SendFail();
190: 
191:         return share;
192:     }
```

As a result, `withdraw()` would revert unexpectedly when it should work.

**Attack Scenario**\
1. Alice deposited 10 eth to the pool and received 10 eEth.
2. Sometime later, the pool earned some profits and Alice can withdraw 11 eth from her 10 eEth.
3. She requests to withdraw 11 eth and `withdraw(Alice, 11 eth)` is called.
4. Then at L176, `share = 10 eEth` but it will revert at L178 because `eETH.balanceOf(msg.sender) < _amount = 11 eth`.


_Trimmed to 38 lines — full report: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/19_
