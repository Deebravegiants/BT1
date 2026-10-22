# [H] Cross-Chain Withdrawal Accounting Corruption

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23288
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Withdrawals can effectively only happen on the primary chain after any yield has accrued  
Description: During round rolls, yield is only realized on the primary chain in SherpaVault::_adjustBalanceAn-  
dEmit. This leaves the system in a problematic state if withdrawals happens on another chain.  
Imagine the scenario: there's 500 + 500 deposits of SherpaUSD on chain A and B, A being primary. 100 Sher-  
paUSD is added as yield on A. The balance is 500 + 600, global total 1100 giving a share price of 1.1. Alice,  
who has half the total shares decides do withdraw on chain B, giving her 550 SherpaUSD (USDC). Since this isn't  
available on chain B, the protocol needs to rebalance 50 SherpaUSD from A to B.  
They do this by calling SherpaUSD::ownerBurn(50) on chain A followed by SherpaUSD::ownerMint(50) on chain  
B. This will store 50 in both approvedTotalStakedAdjustment and approvedAccountingAdjustment on both  
chains. The latter one being the issue.  
Once SherpaVault::adjustTotalStaked is called by the operator, the rebalance of SherpaUSD is done, and Al-  
ice can effectively withdraw. However, there's no way to clear the state in approvedAccountingAdjustment as no  
shares were ever moved. If SherpaVault::adjustAccountingSupply is called, it will corrupt the accountingSup-  
ply as no shares were ever moved. So the states of approvedAccountingAdjustment are effectively permanently  
corrupted as consumeAccountingApproval can only be cleared from the vault.  
In addition to this, if SherpaVault::adjustAccountingSupply was called on chain A, accountingSupply would be  
decremented and the accountingSupply subtraction in function _unstake() would underflow on chain A, hence  
bricking funds.  
Impact: Withdrawals can only safely happen on the primary chain as soon as any yield is accrued. If yield is  
withdraw from the secondary chain that will corrupt either SherpaUSD.approvedAccountingAdjustment or Sher-  
paVault.accountingSupply on both chains.

## Recommendation
Consider split approval modes. Introduce explicit asset-only rebalancing (set ap-  
provedTotalStakedAdjustment without setting approvedAccountingAdjustment) and a share-sync mode (set  
both).
