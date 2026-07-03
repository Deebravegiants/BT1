### Title
Stale `rsETHPrice` Exploitable via Deposit → `updateRSETHPrice()` → Instant-Withdraw Sandwich — (File: `contracts/LRTOracle.sol`)

---

### Summary

`LRTOracle` stores a cached `rsETHPrice` that is only updated when `updateRSETHPrice()` is called. Because that function is **public** and deposits use the cached (potentially stale) price to mint rsETH, an unprivileged attacker can sandwich the price update: deposit at the stale (lower) price, call `updateRSETHPrice()` to push the price to its true higher value, then immediately withdraw at the inflated price — extracting yield that belongs to existing rsETH holders.

---

### Finding Description

`LRTOracle.updateRSETHPrice()` is an unrestricted public function: [1](#0-0) 

It writes the result of `_updateRsETHPrice()` into the storage variable `rsETHPrice`: [2](#0-1) 

Every deposit reads this **stored** value — not a freshly computed one: [3](#0-2) 

Withdrawals (both queued and instant) also read the stored value: [4](#0-3) 

Between any two calls to `updateRSETHPrice()`, staking rewards cause the true TVL to exceed `rsethSupply × rsETHPrice`. During this window the stored price is **below** the fair price. An attacker can:

1. **Deposit** `D` ETH at the stale price `P_stale` → receives `D / P_stale` rsETH (more than fair).
2. **Call** `updateRSETHPrice()` → stored price rises to `P_actual > P_stale`.
3. **Instantly withdraw** (if `isInstantWithdrawalEnabled` is set) the rsETH at `P_actual` → receives `(D / P_stale) × P_actual > D` ETH.

Net profit ≈ `D × (P_actual − P_stale) / P_stale`, funded entirely by diluting existing rsETH holders' accrued yield.

The `_updateRsETHPrice()` logic computes `previousTVL` using the **post-deposit** rsETH supply multiplied by the **stale** price: [5](#0-4) 

This means the attacker's deposit is silently absorbed into the "reward" baseline, and the protocol fee is charged on the combined amount rather than only on the genuine staking reward — further obscuring the extraction.

For the standard withdrawal path the 8-day delay applies, but `instantWithdrawal` removes it entirely when enabled: [6](#0-5) 

---

### Impact Explanation

Existing rsETH holders lose a portion of their accrued staking yield proportional to the attacker's deposit size and the staleness of `rsETHPrice`. For a 1 000 ETH deposit and one day of staleness at ~4 % APY the profit is ≈ 1.1 ETH per attack cycle. With instant withdrawal enabled the cycle collapses to a single block, making repeated extraction trivial. This constitutes **theft of unclaimed yield** (High) and, at scale, approaches **protocol insolvency** (Critical) as the yield pool is continuously drained.

---

### Likelihood Explanation

`rsETHPrice` is stale during every interval between keeper calls. The public `updateRSETHPrice()` means the attacker controls exactly when the price snaps to its true value. No privileged role is required. The only gating conditions are: (a) instant withdrawal must be enabled for the target asset, and (b) the `LRTUnstakingVault` must hold sufficient liquidity — both normal operational states. Likelihood is **Medium**.

---

### Recommendation

1. **Atomically update the price inside `depositETH`/`depositAsset`** before computing `rsethAmountToMint`, so the mint always uses the freshest price.
2. Alternatively, **compute the mint amount from the live TVL** rather than the cached `rsETHPrice`, eliminating the stale-read window entirely.
3. If a cached price must be kept, **restrict `updateRSETHPrice()` to a keeper role** and enforce a minimum update interval so the sandwich window cannot be opened on demand.
4. Add a **deposit-then-withdraw cooldown** (e.g., block-number lock) to prevent same-block or same-transaction round-trips.

---

### Proof of Concept

```
State: TVL = 110 ETH, rsETH supply = 100, rsETHPrice (stored) = 1.00 ETH/rsETH
       (10 ETH of staking rewards have accrued; price not yet updated)

Step 1 – depositETH(10 ETH):
  rsethAmountToMint = 10e18 * 1e18 / 1e18 = 10 rsETH   ← uses stale price
  TVL = 120 ETH, supply = 110

Step 2 – updateRSETHPrice():
  previousTVL = 110 * 1.00 = 110 ETH
  totalETHInProtocol = 120 ETH
  newRsETHPrice = 120 / 110 ≈ 1.0909 ETH/rsETH   ← stored

Step 3 – instantWithdrawal(ETH, 10 rsETH):
  assetAmountUnlocked = 10 * 1.0909 / 1 ≈ 10.909 ETH
  userAmount ≈ 10.909 ETH (minus fee)

Attacker net: deposited 10 ETH, received ≈ 10.909 ETH → profit ≈ 0.909 ETH
Existing holders: each rsETH now worth 1.0909 instead of 1.10 ETH → ~0.91 ETH stolen from them
``` [7](#0-6) [8](#0-7) [9](#0-8)

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
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

**File:** contracts/LRTOracle.sol (L313-313)
```text
        rsETHPrice = newRsETHPrice;
```

**File:** contracts/LRTDepositPool.sol (L506-521)
```text
    function getRsETHAmountToMint(
        address asset,
        uint256 amount
    )
        public
        view
        override
        returns (uint256 rsethAmountToMint)
    {
        // setup oracle contract
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L212-253)
```text
    function instantWithdrawal(
        address asset,
        uint256 rsETHUnstaked,
        string calldata referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedAsset(asset)
        onlySupportedStrategy(asset)
        onlyInstantWithdrawalAllowed(asset)
    {
        if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
            revert InvalidAmountToWithdraw();
        }
        if (IERC20(lrtConfig.rsETH()).balanceOf(msg.sender) < rsETHUnstaked) revert NotEnoughRsETH();
        uint256 assetAmountUnlocked = getExpectedAssetAmount(asset, rsETHUnstaked);
        IRSETH(lrtConfig.rsETH()).burnFrom(address(msg.sender), rsETHUnstaked);
        ILRTUnstakingVault unstakingVault = ILRTUnstakingVault(lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT));
        if (assetAmountUnlocked > unstakingVault.getAssetsAvailableForInstantWithdrawal(asset)) {
            revert CantInstantWithdrawMoreThanAvailable();
        }

        unstakingVault.redeem(asset, assetAmountUnlocked);

        uint256 fee = (assetAmountUnlocked * instantWithdrawalFee) / 10_000;
        uint256 userAmount = assetAmountUnlocked - fee;

        address feeRecipient = instantWithdrawalFeeRecipient;
        if (feeRecipient == address(0)) {
            // Backwards-compatible default: send fees to the protocol treasury
            feeRecipient = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
        }
        if (fee > 0) {
            _transferAsset(asset, feeRecipient, fee);
            emit InstantWithdrawalFeeCollected(msg.sender, asset, fee);
        }

        _transferAsset(asset, msg.sender, userAmount);
        emit ReferralIdEmitted(referralId);
        emit AssetWithdrawalFinalized(msg.sender, asset, rsETHUnstaked, userAmount);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L590-594)
```text
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
    }
```
