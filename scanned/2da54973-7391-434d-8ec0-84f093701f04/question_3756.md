# Q3756: updateRSETHPrice Allowance Race Price Update queued P3756

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and change ERC20 allowance/balance between calculation and transfer using supported token behavior, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that protocol mints/burns only after actual spendable value is secured; specifically, price update must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to direct theft of user funds? Probe condition: queued buffer route; amount case 0.01 ether; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: change ERC20 allowance/balance between calculation and transfer using supported token behavior; validation style: attacker-created state followed by an honest operator action; probe condition: queued buffer route; amount case 0.01 ether; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use operator-normalization follow-up to exercise the allowance race path against updateRSETHPrice and look for price update breaking value conservation or liveness.
- Invariant to test: protocol mints/burns only after actual spendable value is secured; specifically, price update must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: queued buffer route; amount case 0.01 ether; timing immediately after direct ETH donation; caller model EOA caller.
