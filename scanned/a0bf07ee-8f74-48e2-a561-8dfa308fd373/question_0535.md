# Q535: depositAsset Oracle Decimal Mismatch Mint Rate withdrawal P0535

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and choose an asset flow whose oracle precision differs from 1e18 assumptions, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that all share/asset conversions preserve value despite decimals; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to temporary freezing of funds? Probe condition: withdrawal request nonce route; amount case 0.001 ether; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: choose an asset flow whose oracle precision differs from 1e18 assumptions; validation style: an attacker contract as msg.sender or recipient; probe condition: withdrawal request nonce route; amount case 0.001 ether; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the oracle decimal mismatch path against depositAsset and look for mint rate breaking value conservation or liveness.
- Invariant to test: all share/asset conversions preserve value despite decimals; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: write a Foundry invariant that deposits then compares minted rsETH to normalized asset value and totalSupply backing. Use probe condition: withdrawal request nonce route; amount case 0.001 ether; timing same block after updateRSETHPrice; caller model EOA caller.
