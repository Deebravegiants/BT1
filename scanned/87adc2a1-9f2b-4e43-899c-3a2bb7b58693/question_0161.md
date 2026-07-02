# Q161: depositETH Highest Price Ratchet Fee Mint ETH P0161

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and cause highestRsethPrice to ratchet from donated or transient balances then later reverse, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that price protection cannot freeze funds or make withdrawals insolvent from transient TVL; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to protocol insolvency? Probe condition: ETH sentinel route; amount case 0.1 ether; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: cause highestRsethPrice to ratchet from donated or transient balances then later reverse; validation style: several attacker accounts creating adjacent requests; probe condition: ETH sentinel route; amount case 0.1 ether; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the highest-price ratchet path against depositETH and look for fee mint breaking value conservation or liveness.
- Invariant to test: price protection cannot freeze funds or make withdrawals insolvent from transient TVL; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: track protocol fee receiver, rsETH supply, and TVL before/after updateRSETHPrice across period boundaries Use probe condition: ETH sentinel route; amount case 0.1 ether; timing same block before updateRSETHPrice; caller model EOA caller.
