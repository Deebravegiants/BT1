# [H] Attacker could exploit user DCA order for personal gain

## Summary
Severity: High
Reporter: 0xyPhilic
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L163-L238
Type: audit-issue

## Details
# Attacker could exploit user DCA order for personal gain

## Summary

Currently a user can create a DCA order on the `DCA.vy` token contract to swap any token for another via UniswapV3 at specified intervals by invoking `post_dca_order` function. This order can be later executed by a Keeper or any other user via the `execute_dca_order` function by passing the `path` and `fees` for the UniswapV3 pool through which the order will be executed and as long as enough time has passed from the previous execution and the `max_number_of_executions` is not reached.

## Vulnerability Detail

The problem here arises from the option of the `executor` of the order to specify the `path` and `fees` through which the order will be routed via the UniswapV3 SwapRouter or simply put to specify the UniV3 pool through which the order will be executed. This allows a malicious user to create a new pool on UniswapV3 for the pair as long as it does not exist with false data regarding the price of the token or use an existing pool with wrong price data and route the execution of the order through that pool. 

Imagine the following situation:

Alice posts a DCA order to buy MATIC with ARB with the following parameters:
- _token_in: ARB
- _token_out: MATIC
- _amount_in_per_execution: 100 ARB
- _seconds_between_executions: 86400 (1 day)
- _max_number_of_executions: 11 (in order to spend 1k ARB)
- _max_slippage: 500 (0.5%)
- _twap_length: 300

Now a malicious users sees Alice DCA order and decides to take advantage and steal some tokens, by doing the following:

- Create an MATIC/ARB pool on UniswapV3 by setting the price of ARB/MATIC to an undesirable value (or use an existing pool with faulty price data to provide liquidity to)
- Execute Alice DCA order through the above mentioned pool
- Pull out the liquidity and sell the 100 ARB tokens in a regular and stable pool with accurate pricing

The `min_amount_out` is calculated during the execution of the order and uses the pool selected by the attacker so the TWAP returned would actually be a wrong one, but won't impact the overall swap as long as the attacker provide enough liquidity to avoid the `max_slippage` set by the user. 

Note that the above scenario can be done in a single transaction from the attacker via a created SC. Also if the order is big enough the attacker could use a FlashLoan to acquire the liquidity needed to execute the order of the user at an undesirable rate.

Below you can see two screenshots of two MATIC/ARB pools on UniswapV3, one of which is the most desirable and the other with faulty price data:

1/ Faulty price data pool - 1 ARB = ~1.19 MATIC

![maticperarb](https://github.com/sherlock-audit/2023-06-unstoppable-0xyPhilic/assets/60351561/fcacaf1a-309c-4e49-a559-bc0234874cf8)

2/ Regular pool with significant TVL - 1 ARB = ~ 1.68 MATIC:

![maticperarbregular](https://github.com/sherlock-audit/2023-06-unstoppable-0xyPhilic/assets/60351561/67bc355c-9fbc-4a12-95c0-b4aba3027959)

## Impact

An attacker could force the DCA order of a user to go through an undesirable rate which significantly profits the attacker on behalf of the user.

## Code Snippet

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L163-L238

## Tool used

Manual Review / Foundry

## Recommendation

There are two possible approaches in resolving this issue:

1. Allow the user to specify the `path` and `fees` during the `post_dca_order` function invocation. This would leave the execution open to anyone and would simply calculate the `min_tokens_out` based on the user specified `path` and `fees`.

2. To ease the UX you can split the posting of DCA order in the UI into 2:
2.1. Simple DCA without multihop i.e. ARB --> MATIC. This does not require the user to specify a `path` and `fee` tier, but you'll have to use the `exactInputSingle` function on the UniswapV3 Router within the `execute_dca_order` when `path` and `fee` is not specified (could be set to 0 values), which will execute the trade through the best available pool
2.2. Complex DCA with multihop i.e. ARB --> WBTC --> MATIC, which would require the user to specify the `path` and `fee` in order to avoid the potential attack (point 1).
