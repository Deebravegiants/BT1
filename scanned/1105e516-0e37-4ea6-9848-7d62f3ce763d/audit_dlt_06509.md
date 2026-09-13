# [H] User may lost assets by depositing at FM_Rebasing_v1 funding manager

## Summary
Severity: High
Chain: Smart contract
Component: Inverter-Network
Published: 2024-06-05
Source: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/38
Type: hats-finding

## Details
**Github username:** @MehdiKarimi81
**Twitter username:** --
**Submission hash (on-chain):** 0xd9d411a282256761bd65d7635df5422e8b5c36d22a3ecf70eb815c23f477c5ae
**Severity:** high

**Description:**
**Description**\
orcehstrator can transfer assets from funding manager, so it's nessecirily to rebase user balances after every transfer ( updating _bitsPerToken ), it happes via `_rebase` function before every mint or burn, if supply target is zero `_rebase` wouldn't update _bitsPerToken and simply returns, since it's viable to have active bits but no supply target it leads to loss for new depositor, for example we have 1000 active bits + 500 supply target, in this case _bitsPerTokens would be 2, orchestrator transfers out 500 assets from funding manager and making supply target 0, now if a user tries to deposit, `_rebase` won't update _bitsPerTokens and it remains 2, after deposing if he decides to redeem he would receive less tokens since _bitsPerTokens would be updated before burn, part of deposited assets has been distributed between other users.

**Attack Scenario**\
1 - There are 1000 active bits + 500 supply target in funding manager ( _bitsPerToken is 2 ) 
2 - Orchestrator transfers out 500 assets from funding manager 
3 - User deposits 1000 assets and receives 2000 bits 
4 - User burns 2000 bits, `_rebase` would update _bitsPerTokens to 3 so he would receive 633.333 assets which is a loss for this user
