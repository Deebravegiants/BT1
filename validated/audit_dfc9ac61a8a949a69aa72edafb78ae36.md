Audit Report

## Title
Unrestricted Public `updateRSETHPrice()` With No Minimum Interval Enables Deposit-Before-Update Sandwich to Steal Yield From Existing rsETH Holders - (File: contracts/LRTOracle.sol)

## Summary
`LRTOracle.updateRSETHPrice()` is declared `public whenNotPaused` with no cooldown, no timestamp guard, and no role restriction. Because `LRTDepositPool.getRsETHAmountToMint()` divides by the stored `rsETHPrice` rather than a freshly computed value, an attacker can atomically deposit at a stale (below-true) price and then call `updateRSETHPrice()` in the same transaction, minting excess rsETH and diluting the yield that should have accrued to existing holders.

## Finding Description
`LRTOracle.updateRSETHPrice()` is callable by any address with no interval restriction:

```solidity
// contracts/LRTOracle.sol L87-89
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
```

`LRTDepositPool.getRsETHAmountToMint()` reads the stored `rsETHPrice` state variable directly:

```solidity
// contracts/LRTDepositPool.sol L520
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

Because `rsETHPrice` is in the denominator, a stale (lower-than-true) price inflates `rsethAmountToMint`. The price is only updated when `updateRSETHPrice()` or `updateRSETHPriceAsManager()` is explicitly called; between calls it is stale.

**Exploit flow (concrete numbers, zero fee for clarity):**

| State | rsETHPrice | rsethSupply | totalETHInProtocol |
|---|---|---|---|
| Before (stale) | 1.000 ETH | 1000 rsETH | 1010 ETH (rewards accrued) |
| After attacker deposits 100 ETH at stale price | 1.000 ETH | 1100 rsETH | 1110 ETH |
| After attacker calls `updateRSETHPrice()` | 1110/1100 ≈ 1.00909 ETH | 1100 rsETH | 1110 ETH |

- Attacker received 100 rsETH; at the corrected price these are worth ≈ 100.909 ETH → **profit ≈ 0.909 ETH**.
- Existing holders' 1000 rsETH is now worth ≈ 1009.09 ETH instead of 1010 ETH → **loss ≈ 0.909 ETH**.

The `pricePercentageLimit` guard at lines 252–266 does not block this attack: it only reverts if the new price exceeds `highestRsethPrice` by more than the configured threshold. In the attack the new price (≈1.00909) is *lower* than the true pre-attack price (1.01), so the increase from `highestRsethPrice` (1.0) is smaller than it would have been without the attack, making the threshold less likely to trigger. When `pricePercentageLimit == 0` (the default after initialization) the check is entirely disabled.

The `nonReentrant` guard on `depositETH()` does not prevent calling `updateRSETHPrice()` after the deposit completes within the same transaction, as they are separate external calls.

`_updateRsETHPrice()` computes `previousTVL` as `rsethSupply.mulWad(rsETHPrice)` using the stale price and the already-inflated supply, so the "reward" detected is only the pre-existing accrued yield — the attacker's over-minted rsETH is silently absorbed.

## Impact Explanation
Existing rsETH holders suffer concrete, quantifiable theft of unclaimed yield. When the attacker mints rsETH at a stale below-true price, the total rsETH supply increases by more than the proportional TVL contribution. After the price update, the attacker holds rsETH worth more than what they deposited, at the direct expense of all other holders whose share of the TVL is reduced. This matches the allowed impact: **High — Theft of unclaimed yield**.

## Likelihood Explanation
EigenLayer staking rewards accrue continuously, so `rsETHPrice` is always at least slightly stale between updates. The attack requires no special permissions — only the ability to deploy a contract that calls `depositETH()` followed by `updateRSETHPrice()` atomically. Profit scales with deposit size and the magnitude of the stale price gap. The attack is repeatable every time rewards accrue and is executable by any unprivileged external user.

## Recommendation
Introduce a minimum interval between permissionless `updateRSETHPrice()` calls:

```solidity
uint256 public lastPriceUpdateTimestamp;
uint256 public constant MIN_UPDATE_INTERVAL = 1 hours;

function updateRSETHPrice() public whenNotPaused {
    require(block.timestamp >= lastPriceUpdateTimestamp + MIN_UPDATE_INTERVAL, "Too soon");
    lastPriceUpdateTimestamp = block.timestamp;
    _updateRsETHPrice();
}
```

`updateRSETHPriceAsManager()` can remain unrestricted for emergency use. Additionally, consider computing the rsETH mint amount using a freshly computed price rather than the stored stale value, or require that `updateRSETHPrice()` is called before any deposit in the same block.

## Proof of Concept

```solidity
contract SandwichAttack {
    ILRTDepositPool depositPool;
    ILRTOracle oracle;

    constructor(address _pool, address _oracle) {
        depositPool = ILRTDepositPool(_pool);
        oracle = ILRTOracle(_oracle);
    }

    function attack() external payable {
        // Step 1: Deposit at stale (below-true) rsETHPrice.
        // rsETHPrice is stale because EigenLayer rewards have accrued since last update.
        // rsethAmountToMint = (msg.value * assetPrice) / rsETHPrice (stale, lower)
        // → attacker receives MORE rsETH than the true exchange rate warrants.
        depositPool.depositETH{value: msg.value}(0, "");

        // Step 2: Update price in the same transaction.
        // rsETHPrice is now corrected upward.
        // Attacker holds rsETH minted at the old lower price → worth more than deposited.
        // Existing holders' share of TVL is diluted by exactly the attacker's excess.
        oracle.updateRSETHPrice();
    }
}
```

**Foundry fork test plan:**
1. Fork mainnet at a block where EigenLayer rewards have accrued since the last `updateRSETHPrice()` call.
2. Record `oracle.rsETHPrice()` (stale) and compute the true price via `_getTotalEthInProtocol() / rsethSupply`.
3. Deploy `SandwichAttack`, call `attack{value: 100 ether}()`.
4. Assert attacker's rsETH balance × new `rsETHPrice` > 100 ether (profit confirmed).
5. Assert existing holders' rsETH × new `rsETHPrice` < their pre-attack ETH entitlement (dilution confirmed). [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L244-250)
```text
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
        }

        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/LRTOracle.sol (L252-266)
```text
        if (newRsETHPrice > highestRsethPrice) {
            // check if the price is above the threshold
            uint256 priceDifference = newRsETHPrice - highestRsethPrice;
            // pricePercentageLimit is in 1e18 precision (100% = 1e18, 1% = 1e16)
            bool isPriceIncreaseOffLimit =
                pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);

            // check if the price difference is above the threshold
            if (isPriceIncreaseOffLimit) {
                // if sender has a manager role, this doesn't revert.
                // if not, it reverts as price went above the threshold
                if (!IAccessControl(address(lrtConfig)).hasRole(LRTConstants.MANAGER, msg.sender)) {
                    revert PriceAboveDailyThreshold();
                }
            }
```

**File:** contracts/LRTOracle.sol (L313-313)
```text
        rsETHPrice = newRsETHPrice;
```

**File:** contracts/LRTDepositPool.sol (L515-521)
```text
        // setup oracle contract
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```
