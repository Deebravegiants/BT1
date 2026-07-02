# Q306: depositETH Cross Contract Stale Read Mint Rate LRTOracle P0306

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and make one contract read another contract before its state reflects a prior step in the same attack sequence, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that cross-contract accounting snapshots cannot be inconsistent enough to steal or freeze funds; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to direct theft of user funds? Probe condition: LRTOracle price route; amount case available liquidity minus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: make one contract read another contract before its state reflects a prior step in the same attack sequence; validation style: compare many dust calls against one large call; probe condition: LRTOracle price route; amount case available liquidity minus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the cross-contract stale read path against depositETH and look for mint rate breaking value conservation or liveness.
- Invariant to test: cross-contract accounting snapshots cannot be inconsistent enough to steal or freeze funds; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: write a Foundry invariant that deposits then compares minted rsETH to normalized asset value and totalSupply backing. Use probe condition: LRTOracle price route; amount case available liquidity minus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.
