# Q152: depositETH Oracle Decimal Mismatch Deposit Limit Aave P0152

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and choose an asset flow whose oracle precision differs from 1e18 assumptions, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that all share/asset conversions preserve value despite decimals; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to failure to deliver promised returns without principal loss? Probe condition: Aave aWETH liquidity route; amount case 0.01 ether; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: choose an asset flow whose oracle precision differs from 1e18 assumptions; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: Aave aWETH liquidity route; amount case 0.01 ether; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the oracle decimal mismatch path against depositETH and look for deposit limit breaking value conservation or liveness.
- Invariant to test: all share/asset conversions preserve value despite decimals; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: Aave aWETH liquidity route; amount case 0.01 ether; timing same block before updateRSETHPrice; caller model EOA caller.
