# Q1018: receiveFromRewardReceiver Malformed Referral Payload Fee Mint daily P1018

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and supply very large or unusual referralId data on hot user flows, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that unbounded calldata cannot create block-stuffing or stop critical withdrawals; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to theft of unclaimed yield? Probe condition: daily fee mint limit route; amount case 31.999999 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: supply very large or unusual referralId data on hot user flows; validation style: stateful fuzzing over deposit, update price, withdraw, unlock, complete; probe condition: daily fee mint limit route; amount case 31.999999 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use stateful invariant fuzz to exercise the malformed referral payload path against receiveFromRewardReceiver and look for fee mint breaking value conservation or liveness.
- Invariant to test: unbounded calldata cannot create block-stuffing or stop critical withdrawals; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: High. Theft of unclaimed yield
- Fast validation: track protocol fee receiver, rsETH supply, and TVL before/after updateRSETHPrice across period boundaries Use probe condition: daily fee mint limit route; amount case 31.999999 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
