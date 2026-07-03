### Title
Stale `rsETHPrice` After Price Oracle Swap Allows Depositors to Mint Excess rsETH — (File: `contracts/LRTOracle.sol`)

---

### Summary

`LRTOracle.updatePriceOracleFor()` replaces the price oracle for an asset without first syncing the cached `rsETHPrice`. This is the direct analog of M-14: a reference address is changed while a local cached state is stale, and the stale value is then used as the source of truth, producing an unexpected and exploitable outcome.

---

### Finding Description

`LRTOracle` stores `rsETHPrice` as a local cached variable that is only updated when `updateRSETHPrice()` / `_updateRsETHPrice()` is explicitly called. [1](#0-0) 

`updatePriceOracleFor()` swaps the oracle address for an asset immediately, with no prior sync of `rsETHPrice`: [2](#0-1) 

After the swap, `getAssetPrice(asset)` immediately returns the **new** oracle's price, while `rsETHPrice` still reflects the **old** oracle's price. These two values are consumed together in `LRTDepositPool.getRsETHAmountToMint()`: [3](#0-2) 

And in `LRTWithdrawalManager.getExpectedAssetAmount()`: [4](#0-3) 

**Structural parallel to M-14:**

| M-14 (Hats Protocol) | LRT-rsETH analog |
|---|---|
| Toggle contract returns `false` (hat off) | New price oracle returns higher price P2 |
| Local `hat.config` is stale (`true`) | Local `rsETHPrice` is stale (computed with old P1) |
| Toggle address changed → stale local state takes effect | Oracle address changed → stale `rsETHPrice` used for minting |
| Hat unexpectedly becomes active | Depositor mints excess rsETH |

---

### Impact Explanation

When the oracle for asset A is changed from one returning P1 to one returning P2 > P1, and `rsETHPrice = R` has not yet been updated:

- `getRsETHAmountToMint` = `amount × P2 / R`
- Correct value (after sync) = `amount × P2 / R′` where `R′ > R`

The depositor receives more rsETH than they are entitled to. After `updateRSETHPrice()` is called and `rsETHPrice` rises to `R′`, the attacker initiates a withdrawal. `getExpectedAssetAmount` = `rsETHHeld × R′ / P2`, which exceeds the original deposit. The excess is extracted from the pool, constituting **direct theft of funds from existing rsETH holders**.

**Allowed impact**: Critical — direct theft of user funds at-rest.

---

### Likelihood Explanation

- Requires admin to call `updatePriceOracleFor()`, which is a routine operational action (oracle upgrades, fixing stale feeds).
- The attacker does not need to compromise the admin; they only need to observe the oracle-change transaction in the mempool and front-run the subsequent `updateRSETHPrice()` call.
- `updateRSETHPrice()` is a public, permissionless function — the admin cannot atomically change the oracle and sync the price in a single transaction without a dedicated wrapper. [5](#0-4) 

---

### Recommendation

`updatePriceOracleFor()` (and `updatePriceOracleForValidated()`) should call `_updateRsETHPrice()` **before** writing the new oracle address, ensuring `rsETHPrice` is synced to the current oracle's price before the new oracle takes effect. This is the direct analog of the M-14 fix (calling `checkHatToggle()` before changing the toggle address). [6](#0-5) 

---

### Proof of Concept

**Setup:**
- Asset A oracle returns P1 = 1.0 ETH/token; asset A is 50% of total TVL.
- `rsETHPrice = R = 1.05 ETH/rsETH` (last synced).

**Attack:**
1. Admin broadcasts `updatePriceOracleFor(assetA, newOracle)` where `newOracle.getAssetPrice(assetA) = P2 = 1.1 ETH/token`.
2. Attacker observes the transaction and front-runs the subsequent `updateRSETHPrice()` call.
3. Attacker calls `depositAsset(assetA, 1000e18, 0)`.
4. `rsethAmountToMint = 1000e18 × 1.1e18 / 1.05e18 ≈ 1047.6 rsETH` — using stale `rsETHPrice`. [3](#0-2) 

5. `updateRSETHPrice()` is called; `rsETHPrice` updates to `R′ = 1.05 × (1 + 0.5 × 0.1) = 1.1025 ETH/rsETH`. [7](#0-6) 

6. Attacker calls `initiateWithdrawal(assetA, 1047.6e18)`.
7. `expectedAssetAmount = 1047.6 × 1.1025 / 1.1 ≈ 1050 tokens`.
8. After the withdrawal delay, attacker receives ≈1050 tokens having deposited 1000 tokens — **≈5% profit extracted from existing rsETH holders**. [8](#0-7)

### Citations

**File:** contracts/LRTOracle.sol (L26-31)
```text
    mapping(address asset => address priceOracle) public override assetPriceOracle;

    uint256 public override rsETHPrice;
    uint256 public pricePercentageLimit;
    uint256 public highestRsethPrice;

```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L101-119)
```text
    function updatePriceOracleForValidated(address asset, address priceOracle) external onlyLRTAdmin {
        // Sanity check: oracle price must have precision between 1e16 and 1e19
        uint256 price = IPriceFetcher(priceOracle).getAssetPrice(asset);
        if (price > 1e19 || price < 1e16) {
            revert InvalidPriceOracle();
        }
        updatePriceOracleFor(asset, priceOracle);
    }

    /// @dev add/update the price oracle of any asset
    /// @dev only onlyLRTAdmin is allowed
    /// @param asset asset address for which oracle price needs to be added/updated
    function updatePriceOracleFor(address asset, address priceOracle) public onlyLRTAdmin {
        if (lrtConfig.isSupportedAsset(asset)) {
            UtilLib.checkNonZeroAddress(priceOracle);
        }
        assetPriceOracle[asset] = priceOracle;
        emit AssetPriceOracleUpdate(asset, priceOracle);
    }
```

**File:** contracts/LRTOracle.sol (L214-250)
```text
    function _updateRsETHPrice() internal {
        address rsETHTokenAddress = lrtConfig.rsETH();
        uint256 rsethSupply = IRSETH(rsETHTokenAddress).totalSupply();

        if (rsethSupply == 0) {
            rsETHPrice = 1 ether;
            highestRsethPrice = 1 ether;
            return;
        }

        if (highestRsethPrice == 0) {
            highestRsethPrice = rsETHPrice;
        }

        uint256 previousPrice = rsETHPrice;

        // get total ETH in the protocol (normalized to 1e18)
        uint256 totalETHInProtocol = _getTotalEthInProtocol();

        // calculate previousTVL using rsethSupply multiplied by rsETHPrice
        uint256 previousTVL = rsethSupply.mulWad(rsETHPrice);

        IPausable lrtDepositPool = IPausable(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
        IPausable withdrawalManager = IPausable(lrtConfig.getContract(LRTConstants.LRT_WITHDRAW_MANAGER));

        // determine if the protocol is active (not paused)
        bool protocolPaused = lrtDepositPool.paused() || withdrawalManager.paused() || paused;

        // only take fee if TVL increased and protocol is not paused
        uint256 protocolFeeInETH = 0;
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
        }

        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
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

**File:** contracts/LRTWithdrawalManager.sol (L150-178)
```text
    function initiateWithdrawal(
        address asset,
        uint256 rsETHUnstaked,
        string calldata referralId
    )
        external
        override
        nonReentrant
        whenNotPaused
        onlySupportedAsset(asset)
        onlySupportedStrategy(asset)
    {
        if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
            revert InvalidAmountToWithdraw();
        }

        IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);

        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;

        _addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);

        emit ReferralIdEmitted(referralId);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L580-594)
```text
    function getExpectedAssetAmount(
        address asset,
        uint256 amount
    )
        public
        view
        override
        returns (uint256 underlyingToReceive)
    {
        // setup oracle contract
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
    }
```
