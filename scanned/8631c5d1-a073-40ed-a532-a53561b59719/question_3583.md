# Q3583: updateRSETHPrice Nonce Collision Attempt Fee Mint ETHx P3583

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and create requests across assets/accounts so nonce-derived ids collide or are consumed out of order, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that request ids remain unique per asset and cannot release another user request; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to protocol insolvency? Probe condition: ETHx supported asset route; amount case deposit limit plus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: create requests across assets/accounts so nonce-derived ids collide or are consumed out of order; validation style: an attacker contract as msg.sender or recipient; probe condition: ETHx supported asset route; amount case deposit limit plus 1 wei; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the nonce collision attempt path against updateRSETHPrice and look for fee mint breaking value conservation or liveness.
- Invariant to test: request ids remain unique per asset and cannot release another user request; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: track protocol fee receiver, rsETH supply, and TVL before/after updateRSETHPrice across period boundaries Use probe condition: ETHx supported asset route; amount case deposit limit plus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.
