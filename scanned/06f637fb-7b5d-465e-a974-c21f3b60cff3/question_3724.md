# Q3724: updateRSETHPrice Asset Identity Confusion Price Update rsETH P3724

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and use ETH sentinel, WETH, stETH, ETHx, or unsupported token addresses at branch boundaries, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that ETH and ERC20 branches cannot be confused to transfer or account the wrong asset; specifically, price update must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to permanent freezing of unclaimed yield? Probe condition: rsETH burn route; amount case 0.001 ether; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: use ETH sentinel, WETH, stETH, ETHx, or unsupported token addresses at branch boundaries; validation style: a fork test using current deployed balances and supported assets; probe condition: rsETH burn route; amount case 0.001 ether; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the asset identity confusion path against updateRSETHPrice and look for price update breaking value conservation or liveness.
- Invariant to test: ETH and ERC20 branches cannot be confused to transfer or account the wrong asset; specifically, price update must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Medium. Permanent freezing of unclaimed yield
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: rsETH burn route; amount case 0.001 ether; timing immediately after direct ETH donation; caller model EOA caller.
