# Q220: depositETH Claim Replay Reentrancy Swell P0220

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and repeat a claim, completion, or callback after state deletion or transfer occurs, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that one claim/request/NFT/token id settles at most once; specifically, reentrancy must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to permanent freezing of funds? Probe condition: Swell swETH legacy route; amount case 31.999999 ether; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: repeat a claim, completion, or callback after state deletion or transfer occurs; validation style: a fork test using current deployed balances and supported assets; probe condition: Swell swETH legacy route; amount case 31.999999 ether; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the claim replay path against depositETH and look for reentrancy breaking value conservation or liveness.
- Invariant to test: one claim/request/NFT/token id settles at most once; specifically, reentrancy must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: use a callback-capable token/receiver harness and assert no second mint, burn, unlock, or transfer succeeds Use probe condition: Swell swETH legacy route; amount case 31.999999 ether; timing same block before updateRSETHPrice; caller model EOA caller.
