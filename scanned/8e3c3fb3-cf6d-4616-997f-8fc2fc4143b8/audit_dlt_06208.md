# [H] Users can't withdraw their deposits from `LiquidityPool`

## Summary
Severity: High
Chain: Smart contract
Component: ether-fi
Published: 2023-11-10
Source: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/45
Type: hats-finding

## Details
**Github username:** --
**Submission hash (on-chain):** 0x957746d44ea354bc488287fb74e7ad667a71a205f08c522eec23eb90f9d4ec93
**Severity:** high

**Description:**
**Description**
- `LiquidityPool` contract depends on users depositing their ethers and getting `eETH` share tokens as a source of liquidity/funds.

- When a user deposits in the LP; he will be minted `eETH` shares **proportional** to the totalSupply of the shares tokens (`eETH.totalShares()`) and the available ether balance of the pool (`totalPooledEther`).

- As per the current implementation of the `LiquidityPool.withdraw` function: this function can be called only either by the `MembershipManager` contract or the `WithdrawRequestNFT` contract:

      ```solidity
      function withdraw(address _recipient, uint256 _amount) external whenNotPaused returns (uint256) {
            //...some code
            require(msg.sender == address(withdrawRequestNFT) || msg.sender == address(membershipManager), "Incorrect Caller");
            //...some code
      }
      ```

- So if any user wants to withdraw his deposit from the liquidity pool, he must initiate the call from either of the two contracts; otherwis the `withdraw` function will revert with "Incorrect Caller" error message.

**Attack Scenario**
- But it was noticed that `MembershipManager` and `WithdrawRequestNFT` contracts don't implement `LiquidityPool.withdraw` function for deposits withdrawal (only for fee withdrawal when unwrapping `eETH`) ; so there's no way for the user to withdraw his deposit.

**Attachments**

**Revised Code File**
[LiquidityPool.withdraw function](https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/ec7d11c943b545994cd3266b9aa17affde754d9e/src/LiquidityPool.sol#L175-L192)

```diff
   function withdraw(address _recipient, uint256 _amount) external whenNotPaused returns (uint256) {
       uint256 share = sharesForWithdrawalAmount(_amount);
-       require(msg.sender == address(withdrawRequestNFT) || msg.sender == address(membershipManager), "Incorrect Caller");
       if (totalValueInLp < _amount || (msg.sender == address(withdrawRequestNFT) && -ethAmountLockedForWithdrawal < _amount) || eETH.balanceOf(msg.sender) < _amount) revert InsufficientLiquidity();

       if (_amount > type(uint128).max || _amount == 0 || share == 0) revert InvalidAmount();

```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/45_
