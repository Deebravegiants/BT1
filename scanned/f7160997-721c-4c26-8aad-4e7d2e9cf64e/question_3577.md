# Q3577: updateRSETHPrice Nonce Collision Attempt Price Update daily P3577

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and create requests across assets/accounts so nonce-derived ids collide or are consumed out of order, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that request ids remain unique per asset and cannot release another user request; specifically, price update must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to theft of unclaimed yield? Probe condition: daily mint limit route; amount case deposit limit minus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: create requests across assets/accounts so nonce-derived ids collide or are consumed out of order; validation style: one transaction using a contract wallet and controlled calldata; probe condition: daily mint limit route; amount case deposit limit minus 1 wei; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use single transaction to exercise the nonce collision attempt path against updateRSETHPrice and look for price update breaking value conservation or liveness.
- Invariant to test: request ids remain unique per asset and cannot release another user request; specifically, price update must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: High. Theft of unclaimed yield
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: daily mint limit route; amount case deposit limit minus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.
