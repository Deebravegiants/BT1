# Q79: depositETH Rebasing Balance Drift Mint Rate Lido P0079

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and let a supported rebasing LST balance change between request creation and final settlement, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that rebases cannot create unbacked rsETH or freeze queued withdrawals; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to protocol insolvency? Probe condition: Lido stETH unstake route; amount case exact minAmount; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: let a supported rebasing LST balance change between request creation and final settlement; validation style: an attacker contract as msg.sender or recipient; probe condition: Lido stETH unstake route; amount case exact minAmount; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the rebasing balance drift path against depositETH and look for mint rate breaking value conservation or liveness.
- Invariant to test: rebases cannot create unbacked rsETH or freeze queued withdrawals; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: write a Foundry invariant that deposits then compares minted rsETH to normalized asset value and totalSupply backing. Use probe condition: Lido stETH unstake route; amount case exact minAmount; timing same block before updateRSETHPrice; caller model EOA caller.
