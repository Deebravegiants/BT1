# Q19: depositETH Round Down Accumulation Deposit Limit Lido P0019

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that sum of split outputs is not greater than one equivalent unsplit output; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to protocol insolvency? Probe condition: Lido stETH unstake route; amount case 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction; validation style: an attacker contract as msg.sender or recipient; probe condition: Lido stETH unstake route; amount case 1 wei; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the round-down accumulation path against depositETH and look for deposit limit breaking value conservation or liveness.
- Invariant to test: sum of split outputs is not greater than one equivalent unsplit output; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: Lido stETH unstake route; amount case 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.
