# [M] Invariant violation (funds could remain in the vault and a depositor could benefit from it)

## Summary
Severity: Medium
Contest weight: 0.6038
Dataset id: 15567
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There is a violation to one of the main invariants defined by the sponsor - After every action (deposit/withdraw/rebalance/compound), the vault should be cleared of any token balances. Violation of this could allow a subsequent depositor to benefit from it. coming from the compound() function, which withdraws funds from trove, but after that there is a if, where the funds would remain in the contract, if the condition is not met.

Compound functionality is used to reinvest "rewards"(in form if airdrops for example) from GMX, given to the vault contract. The problem here is that if the the balance of the vault, for the given tokenIn after withdrawing tokenA/B from trove is zero, the function terminates with potentially tokens after the withdraw. Another problem is that the function does the check, wether the vault is open and set its state again inside the if statement. All those combined makes it possible for a user to benefit from those tokens.
```solidity
    // Transfer any tokenA/B from trove to vault
    if (self.tokenA.balanceOf(address(self.trove)) > 0) {
      self.tokenA.safeTransferFrom(
        address(self.trove),
        address(this),
        self.tokenA.balanceOf(address(self.trove))
      );
    }
    if (self.tokenB.balanceOf(address(self.trove)) > 0) {
      self.tokenB.safeTransferFrom(
        address(self.trove),
        address(this),
        self.tokenB.balanceOf(address(self.trove))
      );
    }

    uint256 _tokenInAmt = IERC20(cp.tokenIn).balanceOf(address(this));

    // Only compound if tokenIn amount is more than 0
    if (_tokenInAmt > 0) {
    ...
      _alp.tokenAAmt = self.tokenA.balanceOf(address(this));
      _alp.tokenBAmt = self.tokenB.balanceOf(address(this));
    ...
      GMXChecks.beforeCompoundChecks(self);
      self.status = GMXTypes.Status.Compound;
      self.compoundCache.depositKey = GMXManager.addLiquidity(
        self,
        _alp
      );
    }
```

Inside deposit/withdraw functions we send all tokens A/B back to trove and that would prevent the problem, but since compound doesn't check the state of the vault, this transaction could be frontruned, so the withdraw cache is created. After that the compound would left some funds for one of the tokens and then the transaction triggered from callback proccessWithdraw would use this tokens to benefit the depositor.
Imagine the following scenario:
After some time for the protocol functioning now the trove has gained 1000 USDC and 0 WETH (from airdrop for example)
The compound bot is running scheduled transactions once with "tokenIn : USDC", once with "tokenIn : WETH" 

_1._ Bot initiates compound function with "tokenIn : WETH"

_2._ Eve sees that transaction and frontruns it calling a withdraw with "shareAmt : 10, token : USDC"
This transaction set the vault status to "Withdraw"

_3._ Bot enter compound and only withdraw 1000 USDC and 0 WETH. The transaction passes, no matter that the state is "Withdraw"

_4._ Callback function to proccessWithdraw of Eve do check wether received amount is at least minWithdrawTokenAmt, which is not a problem, because the contract transfer the whole balance of USDC (1000 + {amount corresponding to 10 shares})

## Recommendation
Consider adding 'else' statement, which would return withdrawn tokens
```solidity
   if (self.tokenA.balanceOf(address(self.trove)) > 0) {
      self.tokenA.safeTransferFrom(
        address(self.trove),
        address(this),
        self.tokenA.balanceOf(address(self.trove))
      );
    }
    if (self.tokenB.balanceOf(address(self.trove)) > 0) {
      self.tokenB.safeTransferFrom(
        address(self.trove),
        address(this),
        self.tokenB.balanceOf(address(self.trove))
      );
    }

    uint256 _tokenInAmt = IERC20(cp.tokenIn).balanceOf(address(this));

    // Only compound if tokenIn amount is more than 0
    if (_tokenInAmt > 0) {
    ...
    }
    else{
     self.tokenA.safeTransfer(address(self.trove), self.tokenA.balanceOf(address(this)));
     self.tokenB.safeTransfer(address(self.trove), self.tokenB.balanceOf(address(this)));
    }
```
