# Q3475: updateRSETHPrice Round Down Accumulation Pause Race withdrawal P3475

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that sum of split outputs is not greater than one equivalent unsplit output; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to direct theft of user funds? Probe condition: withdrawal request nonce route; amount case daily limit minus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction; validation style: an attacker contract as msg.sender or recipient; probe condition: withdrawal request nonce route; amount case daily limit minus 1 wei; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the round-down accumulation path against updateRSETHPrice and look for pause race breaking value conservation or liveness.
- Invariant to test: sum of split outputs is not greater than one equivalent unsplit output; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: roll state around pause/updateRSETHPrice and assert no burned/committed assets remain unpaid Use probe condition: withdrawal request nonce route; amount case daily limit minus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.
