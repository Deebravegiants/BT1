# Q145: depositETH Oracle Decimal Mismatch Mint Rate rsETH P0145

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and choose an asset flow whose oracle precision differs from 1e18 assumptions, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that all share/asset conversions preserve value despite decimals; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to protocol insolvency? Probe condition: rsETH transfer route; amount case 0.01 ether; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: choose an asset flow whose oracle precision differs from 1e18 assumptions; validation style: one transaction using a contract wallet and controlled calldata; probe condition: rsETH transfer route; amount case 0.01 ether; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use single transaction to exercise the oracle decimal mismatch path against depositETH and look for mint rate breaking value conservation or liveness.
- Invariant to test: all share/asset conversions preserve value despite decimals; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: write a Foundry invariant that deposits then compares minted rsETH to normalized asset value and totalSupply backing. Use probe condition: rsETH transfer route; amount case 0.01 ether; timing same block before updateRSETHPrice; caller model EOA caller.
