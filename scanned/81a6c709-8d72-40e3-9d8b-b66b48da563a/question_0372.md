# Q372: depositETH Unclaimed Yield Diversion Fee Mint Aave P0372

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and time reward send, interest collection, fee minting, or claim settlement to redirect yield, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that unclaimed yield cannot be stolen or permanently frozen by a public caller; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to permanent freezing of funds? Probe condition: Aave aWETH liquidity route; amount case deposit limit minus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: time reward send, interest collection, fee minting, or claim settlement to redirect yield; validation style: attacker-created state followed by an honest operator action; probe condition: Aave aWETH liquidity route; amount case deposit limit minus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use operator-normalization follow-up to exercise the unclaimed-yield diversion path against depositETH and look for fee mint breaking value conservation or liveness.
- Invariant to test: unclaimed yield cannot be stolen or permanently frozen by a public caller; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: track protocol fee receiver, rsETH supply, and TVL before/after updateRSETHPrice across period boundaries Use probe condition: Aave aWETH liquidity route; amount case deposit limit minus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.
