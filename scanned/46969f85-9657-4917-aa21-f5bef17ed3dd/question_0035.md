# Q35: depositETH Round Up Insolvency Mint Rate withdrawal P0035

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and choose amounts just above precision boundaries so liabilities round up while assets round down, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that rsETH liabilities never exceed normalized protocol assets; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to protocol insolvency? Probe condition: withdrawal request nonce route; amount case 2 wei; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: choose amounts just above precision boundaries so liabilities round up while assets round down; validation style: a local supported-token harness with configurable transfer behavior; probe condition: withdrawal request nonce route; amount case 2 wei; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the round-up insolvency path against depositETH and look for mint rate breaking value conservation or liveness.
- Invariant to test: rsETH liabilities never exceed normalized protocol assets; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: write a Foundry invariant that deposits then compares minted rsETH to normalized asset value and totalSupply backing. Use probe condition: withdrawal request nonce route; amount case 2 wei; timing same block before updateRSETHPrice; caller model EOA caller.
