# [H] Fee on transfer tokens will cause users to lose funds

## Summary
Severity: High
Contest weight: 0.7818
Dataset id: 3682
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Some ERC20 tokens, such as USDT, allow for charging a fee any time transfer() or transferFrom() is called. If a contract does not allow for amounts to change after transfers, subsequent transfer operations based on the original amount will revert() due to the contract having an insufficient balance. However, a malicious user could also take advantage of this to steal funds from the pool.

Let's take a look at the deposit() and withdraw() functions. 

```solidity
    function deposit(uint _amount) external {
        TKN.transferFrom(msg.sender, address(this), _amount);
        updateFor(msg.sender);
        balances[msg.sender] += _amount;
    }

    /// @notice withdraw tokens from stake
    /// @param _amount the amount to withdraw
    function withdraw(uint _amount) external {
        updateFor(msg.sender);
        balances[msg.sender] -= _amount;
        TKN.transfer(msg.sender, _amount);
    }
```
Alice sends 100 of FEE token to the contract when calling addToPool().
FEE token contract takes 10% of the tokens (10 FEE).
90 FEE tokens actually get deposit in contract.
_updatePoolBalance(poolId, pools[poolId].poolBalance + amount); will equal 100.
Attacker then sends 100 FEE tokens to the contract
The contract now has 180 FEE tokens but each user has an accounting of 100 FEE.
The attacker then tries to redeem his collateral for the full amount 100 FEE tokens.
The contract will transfer 100 FEE tokens to Bob taking 10 of Alice's tokens with him.
Bob can then deposit back into the pool and repeat this until he drains all of Alice's funds.
When Alice attempts to withdraw the transaction will revert due to insufficient funds.

## Recommendation
Measure the contract balance before and after the call to transfer()/transferFrom() and use the difference between the two as the amount, rather than the amount stated

```solidity
    function deposit(uint _amount) external {
        uint256 balanceBefore = IERC20(TKN).balanceOf(address(this));
        TKN.transferFrom(msg.sender, address(this), _amount);
        uint256 balanceAfter = IERC20(TKN).balanceOf(address(this));
        uint256 amount = balanceAfter - balanceBefore;
        updateFor(msg.sender);
        balances[msg.sender] += amount;
    }
```
Note this implementation is vulnerable to reentrancy so be sure to add a reentrancy guard to this function.
