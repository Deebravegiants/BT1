# Q1782: receiveFromNodeDelegator Malformed Referral Payload Price Update stETH P1782

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and supply very large or unusual referralId data on hot user flows, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that unbounded calldata cannot create block-stuffing or stop critical withdrawals; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to protocol insolvency? Probe condition: stETH supported asset route; amount case 1 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: supply very large or unusual referralId data on hot user flows; validation style: compare many dust calls against one large call; probe condition: stETH supported asset route; amount case 1 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the malformed referral payload path against receiveFromNodeDelegator and look for price update breaking value conservation or liveness.
- Invariant to test: unbounded calldata cannot create block-stuffing or stop critical withdrawals; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: stETH supported asset route; amount case 1 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
