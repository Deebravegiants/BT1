# [M] Noya is not compatible with tokens whose balance changes outside of transfers causing funds to get stuck in the contract

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-noya
Published: 2024-05-17
Source: https://github.com/code-423n4/2024-04-noya-findings/issues/1548
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/accountingManager/AccountingManager.sol#L205
https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/accountingManager/AccountingManager.sol#L205


# Vulnerability details

## Impact
Funds will be stuck in the contract

NOTE: this is entirely different from the _fee on transfer_ [4naly3er report finding](https://github.com/code-423n4/2024-04-noya/blob/main/4naly3er-report.md#m-1-contracts-are-vulnerable-to-fee-on-transfer-accounting-related-issues) which doesn't necessarily state the impact of the issue. 
As a matter of fact, going by the C4 rules, _if an automated report does explain the full impact of the finding and the severity is not judged correctly, but a warden is able to raise it to a higher severity level, then its a fair game_



I am reporting this because the audit FAQ states that ERC20 token balance changes outside of transfers is in scope for this audit


## Proof of Concept
This happens because the balance of the contract is not checked before and after a token is deposit is made

If a core functions of the protocol uses a rebasing token for instance to open positions, some user funds will be stuck in the contract. For simplicity we assume `tokenA` is a token whose balance changes outside of transfers

- Alice and Bod each deposit 1000 `tokenA` in the `AccountingManager` contract without opening positions making a total of 2000 `tokenA`
- Over time the balance of `tokenA` shrinks by say 10%, leaving the `AccountingManager` with 1900 `tokenA`
- Alice calls `AccountingManager::withdraw(...)` before Bob and gets 1000 `tokenA`
- Bob calls `AccountingManager::withdraw(...)` but the call will revert because bobs `WithdrawRequest[bob]` is now more than the balance of the contract.
- Bobs funds are stuck in the contract

Also, some smart contract systems cache token balances (e.g. Balancer, Uniswap-V2), and arbitrary modifications to underlying balances can mean that the contract is operating with outdated information this can affect withdrawals from the strategy.



Likelyhood: High
Impact: High
Severity: High


_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-04-noya-findings/issues/1548_
