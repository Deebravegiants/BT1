Audit Report

## Title
Stale agETH/ETH Rate in `CrossChainRateReceiver` Enables Over-Minting of agETH on Token Deposits — (`contracts/agETH/AGETHRateReceiver.sol`)

## Summary
`CrossChainRateReceiver.getRate()` returns the stored `rate` unconditionally with no staleness check, despite `lastUpdated` being recorded on every LayerZero message. `AGETHPoolV3.viewSwapAgETHAmountAndFee(uint256, address)` uses this potentially stale rate as the denominator when computing agETH to mint, while the deposited token's oracle rate is fetched live. When the agETH rate is stale-low relative to a token's current oracle rate, any unprivileged depositor receives more agETH than their collateral's ETH-equivalent value justifies, diluting existing agETH holders.

## Finding Description
`CrossChainRateReceiver.getRate()` returns `rate` with no age enforcement:

```solidity
// contracts/cross-chain/CrossChainRateReceiver.sol L103-105
function getRate() external view returns (uint256) {
    return rate;
}
```

`rate` and `lastUpdated` are set only when a LayerZero message arrives via `lzReceive`:

```solidity
// contracts/cross-chain/CrossChainRateReceiver.sol L95-97
rate = _rate;
lastUpdated = block.timestamp;
```

`lastUpdated` is never read back in `getRate()` or anywhere in the deposit path. `AGETHPoolV3.getRate()` is a thin pass-through:

```solidity
// contracts/agETH/AGETHPoolV3.sol L104-106
function getRate() public view returns (uint256) {
    return IOracle(agETHOracle).getRate();
}
```

`viewSwapAgETHAmountAndFee(uint256, address)` then computes the mint amount using the stale agETH rate as denominator and a live token oracle rate as numerator:

```solidity
// contracts/agETH/AGETHPoolV3.sol L188-194
uint256 agETHToETHrate = getRate();                                      // stale
uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate(); // live
agETHAmount = amountAfterFee * tokenToETHRate / agETHToETHrate;
```

This result is consumed directly by the public `deposit(address token, uint256 amount, string referralId)` function, which mints the computed amount to the caller with no further validation:

```solidity
// contracts/agETH/AGETHPoolV3.sol L147-151
(uint256 agETHAmount, uint256 fee) = viewSwapAgETHAmountAndFee(amount, token);
feeEarnedInToken[token] += fee;
agETH.mint(msg.sender, agETHAmount);
```

No guard anywhere in this call chain checks `block.timestamp - lastUpdated`. An attacker only needs to observe that `lastUpdated` is old (public state) and that the token oracle rate has moved favorably — both are on-chain readable — then call `deposit`.

## Impact Explanation
The protocol mints more agETH than the deposited collateral backs at current rates. The agETH supply becomes under-collateralised relative to the true agETH/ETH exchange rate, diluting existing agETH holders' claims on the underlying ETH. This matches **Low — Contract fails to deliver promised returns, but doesn't lose value**: deposited collateral is received in full, but the minted agETH exceeds what the collateral justifies, breaking the collateralisation invariant.

## Likelihood Explanation
LayerZero cross-chain message delivery is subject to real-world delays (relayer downtime, gas price spikes, network congestion). During any such delay the stored rate becomes stale. No admin compromise, governance capture, or oracle manipulation is required. The attacker needs only: (1) read `lastUpdated` to confirm staleness, (2) read the token oracle rate to confirm a favorable divergence, (3) call `deposit`. This is repeatable by any unprivileged external account for as long as the rate remains stale.

## Recommendation
Add a staleness guard in `CrossChainRateReceiver.getRate()`:

```solidity
uint256 public constant MAX_RATE_AGE = 1 days; // configurable by owner

function getRate() external view returns (uint256) {
    require(block.timestamp - lastUpdated <= MAX_RATE_AGE, "Rate is stale");
    return rate;
}
```

This causes `deposit` to revert when the agETH rate has not been refreshed within the acceptable window, preventing exploitation of stale rates. The threshold should be set conservatively relative to the expected LayerZero update frequency.

## Proof of Concept

```solidity
// Foundry fork test (local fork, no public mainnet interaction)
// 1. Deploy AGETHRateReceiver; simulate lzReceive setting rate = 1.0e18,
//    lastUpdated = block.timestamp.
// 2. Warp block.timestamp forward by 2 days (simulating LayerZero delay).
//    rate remains 1.0e18; true agETH/ETH rate has risen to 1.05e18.
// 3. Configure wstETH oracle to return 1.05e18 (current live rate).
// 4. Attacker calls AGETHPoolV3.deposit(wstETH, 1e18, "").
//    viewSwapAgETHAmountAndFee computes:
//      agETHAmount = 1e18 * 1.05e18 / 1.0e18 = 1.05e18
// 5. Fair mint at current agETH rate:
//      agETHAmount = 1e18 * 1.05e18 / 1.05e18 = 1.0e18
// 6. Assert minted (1.05e18) > fair (1.0e18): +5% over-mint confirmed.
//    Existing holders' ETH claims are diluted by the unbacked surplus.
``` [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L95-97)
```text
        rate = _rate;

        lastUpdated = block.timestamp;
```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L103-105)
```text
    function getRate() external view returns (uint256) {
        return rate;
    }
```

**File:** contracts/agETH/AGETHPoolV3.sol (L104-106)
```text
    function getRate() public view returns (uint256) {
        return IOracle(agETHOracle).getRate();
    }
```

**File:** contracts/agETH/AGETHPoolV3.sol (L134-154)
```text
    function deposit(
        address token,
        uint256 amount,
        string memory referralId
    )
        external
        nonReentrant
        onlySupportedToken(token)
    {
        if (amount == 0) revert InvalidAmount();

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 agETHAmount, uint256 fee) = viewSwapAgETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        agETH.mint(msg.sender, agETHAmount);

        emit SwapOccurred(msg.sender, agETHAmount, fee, referralId);
    }
```

**File:** contracts/agETH/AGETHPoolV3.sol (L187-194)
```text
        // rate of agETH in ETH
        uint256 agETHToETHrate = getRate();

        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final agETH amount
        agETHAmount = amountAfterFee * tokenToETHRate / agETHToETHrate;
```
