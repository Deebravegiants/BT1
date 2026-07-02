# Q24: depositETH Round Down Accumulation Mint Rate rsETH P0024

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that sum of split outputs is not greater than one equivalent unsplit output; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to protocol insolvency? Probe condition: rsETH burn route; amount case 2 wei; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction; validation style: attacker-created state followed by an honest operator action; probe condition: rsETH burn route; amount case 2 wei; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use operator-normalization follow-up to exercise the round-down accumulation path against depositETH and look for mint rate breaking value conservation or liveness.
- Invariant to test: sum of split outputs is not greater than one equivalent unsplit output; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: write a Foundry invariant that deposits then compares minted rsETH to normalized asset value and totalSupply backing. Use probe condition: rsETH burn route; amount case 2 wei; timing same block before updateRSETHPrice; caller model EOA caller.
