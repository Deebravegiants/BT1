# [M] Users might not be able to withdraw perp profit and loss

## Summary
Severity: Medium
Contest weight: 0.2617
Dataset id: 22454
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Users can deposit any collateral to support their perp positions, however settlement is done in core collateral asset. The problem is the mismatch between the realized profit and loss (which is forced to be in core collateral asset) and unrealized profit and loss (which is theoretical and is not forced to be in core collateral asset). When a lot of deposits are in non-core collateral assets and then some profit is realized, transactions to withdraw this profit will revert, because system won't have enough core collateral asset and there is no way to "force" conversion of deposited assets into core collateral asset.
This means that it's easily possible that users can't withdraw core collateral asset due to protocol not having enough of it, which can happen by itself or crafted by malicious user.
Possible scenario of the issue happening by itself:
1. Alice deposits 10 BTC, Bob deposits 100 ETH, Charlie deposits 5000 USDC (USDC = core collateral asset)
2. Alice opens 1 BTC long position with Bob being the maker (1 BTC short position), at the price of BTC = $10000
3. BTC price rises to $20000. Alice now has unrealized profit of $10000, Bob has unrealized loss of $10000.
4. Alice closes her position against Charlie, realizing 10000 USDC profit.
5. Alice now has 1 BTC + 10000 USDC, Bob has 100 ETH and 1 BTC short position with unrealized loss of 10000 USDC, Charlie has 5000 USDC and 1 BTC long position (with 0 unrealized pnl).
6. Alice tries to withdraw 10000 USDC profit, but transaction reverts, because the protocol only has 5000 USDC.
7. Alice withdraws 5000 USDC. Now Charlie wants to withdraw some of its deposit, but any amount will revert, because protocol has no core collateral deposited at all.
The issue arises when some profit is realized in core collateral, but the loss remains unrealized thus deposited assets are not forced to be converted to core collateral asset.
Possible scenario of the issue being forced by malicious user:
1. Protocol has 1 BTC, 10 ETH and 10000 USDC deposited (USDC = core collateral asset)
2. Malicious user Alice wants to cause panic for protocol users
3. Alice uses 2 subaccounts, depositing 10 BTC into acc#1 and 10 BTC into acc#2
4. Alice uses acc#1 to open 100 BTC long position, and at the same time uses acc#2 to open 100 BTC short position (price = $10000)
5. Alice waits for BTC to rise or fall until either acc#1 or acc#2 is in 10000 USDC profit.
6. For example, BTC has dropped to $9900, acc#1 has 10000 USDC unrealized loss, acc#2 has 10000 USDC unrealized profit.
7. Alice closes and immediately reopens 100 BTC short position in acc#2, withdrawing 10000 USDC of realized profit.
After these steps, Alice can go wreck havoc by saying to users to try to withdraw their core collateral asset, and when transactions revert, this can cause panic and everybody withdrawing and creating negative publicity and reputation: it's always bad when users can not withdraw their assets unexpectedly.
Users might be unable to withdraw any deposited assets or realized profit in core collateral asset. This can happen by itself, or caused by malicious user.
Health calculation includes any deposited asset:
/contracts/libraries/MarginDirective.sol#L94-L100
This means that users can deposit non-core collateral asset to support their open positions, but the profit is realized in core collateral asset:
/contracts/OrderDispatch.sol#L599-L607
This means that protocol might not have enough core collateral asset to pay out the realized profits, when the loss is not yet realized (and the loss can stay unrealized for a long time).

## Recommendation
The solution depends a lot on what the direction the protocol wants to go. Some possible solutions:
• Allow forced settlement of unrealized profit (something similar to auto deleveraging, only soft version to auto settle unrealized profit, converting part of collateral asset into core collateral asset to support unrealized loss when there is not enough core collateral in the system)
• Create some kind of "reserves" fund in core collateral asset, which will be used to cover shortfalls. It might be combined with insurance fund.
