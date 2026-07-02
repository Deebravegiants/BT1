# Q3601: updateRSETHPrice Oracle Decimal Mismatch Pause Race ETH P3601

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and choose an asset flow whose oracle precision differs from 1e18 assumptions, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that all share/asset conversions preserve value despite decimals; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to temporary freezing of funds? Probe condition: ETH sentinel route; amount case 1 wei; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: choose an asset flow whose oracle precision differs from 1e18 assumptions; validation style: one transaction using a contract wallet and controlled calldata; probe condition: ETH sentinel route; amount case 1 wei; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use single transaction to exercise the oracle decimal mismatch path against updateRSETHPrice and look for pause race breaking value conservation or liveness.
- Invariant to test: all share/asset conversions preserve value despite decimals; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: roll state around pause/updateRSETHPrice and assert no burned/committed assets remain unpaid Use probe condition: ETH sentinel route; amount case 1 wei; timing immediately after direct ETH donation; caller model EOA caller.
