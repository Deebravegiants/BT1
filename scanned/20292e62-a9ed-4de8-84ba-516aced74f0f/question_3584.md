# Q3584: updateRSETHPrice Nonce Collision Attempt Pause Race rsETH P3584

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and create requests across assets/accounts so nonce-derived ids collide or are consumed out of order, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that request ids remain unique per asset and cannot release another user request; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to theft of unclaimed yield? Probe condition: rsETH burn route; amount case deposit limit plus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: create requests across assets/accounts so nonce-derived ids collide or are consumed out of order; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: rsETH burn route; amount case deposit limit plus 1 wei; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the nonce collision attempt path against updateRSETHPrice and look for pause race breaking value conservation or liveness.
- Invariant to test: request ids remain unique per asset and cannot release another user request; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: High. Theft of unclaimed yield
- Fast validation: roll state around pause/updateRSETHPrice and assert no burned/committed assets remain unpaid Use probe condition: rsETH burn route; amount case deposit limit plus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.
