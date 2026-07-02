# Q3607: updateRSETHPrice Oracle Decimal Mismatch Highest Price FeeReceiver P3607

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and choose an asset flow whose oracle precision differs from 1e18 assumptions, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that all share/asset conversions preserve value despite decimals; specifically, highest price must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to permanent freezing of unclaimed yield? Probe condition: FeeReceiver reward route; amount case 1 wei; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: choose an asset flow whose oracle precision differs from 1e18 assumptions; validation style: an attacker contract as msg.sender or recipient; probe condition: FeeReceiver reward route; amount case 1 wei; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the oracle decimal mismatch path against updateRSETHPrice and look for highest price breaking value conservation or liveness.
- Invariant to test: all share/asset conversions preserve value despite decimals; specifically, highest price must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Medium. Permanent freezing of unclaimed yield
- Fast validation: write a Foundry stateful test and assert protocol balances, liabilities, and user payouts remain conserved Use probe condition: FeeReceiver reward route; amount case 1 wei; timing immediately after direct ETH donation; caller model EOA caller.
