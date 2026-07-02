# Q221: depositETH Claim Replay Pause Race ETH P0221

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and repeat a claim, completion, or callback after state deletion or transfer occurs, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that one claim/request/NFT/token id settles at most once; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to protocol insolvency? Probe condition: ETH sentinel route; amount case 32 ether; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: repeat a claim, completion, or callback after state deletion or transfer occurs; validation style: several attacker accounts creating adjacent requests; probe condition: ETH sentinel route; amount case 32 ether; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the claim replay path against depositETH and look for pause race breaking value conservation or liveness.
- Invariant to test: one claim/request/NFT/token id settles at most once; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: roll state around pause/updateRSETHPrice and assert no burned/committed assets remain unpaid Use probe condition: ETH sentinel route; amount case 32 ether; timing same block before updateRSETHPrice; caller model EOA caller.
