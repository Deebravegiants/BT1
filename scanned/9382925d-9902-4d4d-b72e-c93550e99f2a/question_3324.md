# Q3324: getETHDistributionData Malformed Referral Payload Price Update rsETH P3324

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and supply very large or unusual referralId data on hot user flows, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that unbounded calldata cannot create block-stuffing or stop critical withdrawals; specifically, price update must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to failure to deliver promised returns without principal loss? Probe condition: rsETH burn route; amount case 0.001 ether; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: supply very large or unusual referralId data on hot user flows; validation style: attacker-created state followed by an honest operator action; probe condition: rsETH burn route; amount case 0.001 ether; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use operator-normalization follow-up to exercise the malformed referral payload path against getETHDistributionData and look for price update breaking value conservation or liveness.
- Invariant to test: unbounded calldata cannot create block-stuffing or stop critical withdrawals; specifically, price update must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: rsETH burn route; amount case 0.001 ether; timing immediately after reward sendFunds; caller model EOA caller.
