# [H] User can avoid paying fees by sending the ETH separately from the swap transaction

## Summary
Severity: High
Contest weight: 0.2866
Dataset id: 22819
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
User can avoid paying fees by sending the ETH separately from the swap transaction When user calls takeTokensAndTrade, it only verifies that enough msg.value is sent for the first swapOp. However, eth -> token swap can happen in multiple consecutive swap operations. If msg.value is not enough to cover the fees prior to the swaps, fees will simply not be taken and transaction will continue. After the swapOps finish, tryToChargeFees will be invoked again. However, this time the amount on which the call will be attempted is the received token amount. Imagine the following scenario: User wishes to swap 1WETH -> 4000 USDC 1. User sends 1 WETH to the contract 2. User calls takeTokensAndTrade with 2 swapOps - first one has amountIn = 40e6 wei, second one has 1e18 - 40e6. msg.value == 40e6. feesTokenAddress == address(0). 3. Fees are calculated as 1% = 0.01 WETH. First tryToChargeFees call fails as msg.value is not enough to cover the fees. 4. Swap execute. 4000 USDC is received (4000e6). 5. tryToChargeFees is called again. However, this time the amount on which fees will be calculated is 4000e6. 1% of that is 40e6. Since msg.value is enough to cover that, 40e6 is paid in fees. In the end the user did a swap for 1 WETH and should've paid 0.01e18 WETH in fees but paid only 40e6 (over 99.9999999% less) Loss of yield

## Recommendation
properly check that enough eth is sent as msg.value
