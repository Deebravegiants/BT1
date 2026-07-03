### Title
`LRTDepositPool#depositAsset` uses a fresh live asset price against a stale cached `rsETHPrice`, allowing depositors to receive excess rsETH at the expense of existing holders — (File: `contracts/LRTDepositPool.sol`)

---

### Summary

`LRTDepositPool.getRsETHAmountToMint()` computes the rsETH to mint using a **fresh, real-time** asset price from `lrtOracle.getAssetPrice(asset)` divided by a **cached, potentially stale** `lrtOracle.rsETHPrice()`. Because `rsETHPrice` is only updated when `updateRSETHPrice()` is explicitly called (off-chain keeper), any time that elapses between oracle updates allows a depositor to receive more rsETH than their proportional fair share, diluting existing holders.

---

### Finding Description

`LRTDepositPool.getRsETHAmountToMint()` computes the rsETH mint amount as:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [1](#0-0) 

- `lrtOracle.getAssetPrice(asset)` calls through to a live Chainlink feed and returns the **current** asset/ETH rate. [2](#0-1) 

- `lrtOracle.rsETHPrice()` returns a **stored state variable** that is only refreshed when `updateRSETHPrice()` is called externally. [3](#0-2) 

`rsETHPrice` is computed inside `_updateRsETHPrice()` as `totalETHInProtocol / rsethSupply`, where `totalETHInProtocol` itself uses `getAssetPrice()` at the moment of the update call. [4](#0-3) 

**The mismatch:** Suppose `rsETHPrice` was last set at time T0 using stETH/ETH = 1.050. By time T1, stETH/ETH has risen to 1.060 (continuous staking rewards). A depositor calling `depositAsset(stETH, amount, ...)` at T1 gets:

```
rsETH minted = amount × 1.060 (fresh) / 1.050 (stale)
             = amount × 1.00952...
```

The fair amount (using the T1-correct rsETH price) would be approximately `amount × 1.060 / 1.060 = amount`. The depositor receives ~0.95% extra rsETH per unit deposited, capturing yield that has accrued to existing holders since the last oracle update.

The deposit path that triggers this is fully permissionless: [5](#0-4) 

`_beforeDeposit` calls `getRsETHAmountToMint` without first refreshing `rsETHPrice`: [6](#0-5) 

---

### Impact Explanation

Every depositor who deposits between two `updateRSETHPrice()` calls, when the underlying LST price has risen, receives more rsETH than their proportional share of the protocol's assets. This excess rsETH is minted out of thin air relative to the stale accounting, diluting the value of all existing rsETH holders. When `updateRSETHPrice()` is eventually called, the new price is computed over a larger rsETH supply than is warranted, permanently reducing the per-token value for existing holders. This constitutes **theft of unclaimed yield** from existing rsETH holders.

**Impact: High — Theft of unclaimed yield.**

---

### Likelihood Explanation

- stETH (and other LSTs) accrue staking rewards continuously, so their ETH price increases every block.
- `updateRSETHPrice()` is called by an off-chain keeper on a periodic schedule (not on every block or every deposit). Any gap between keeper calls creates the window.
- The entry path (`depositAsset`) is fully permissionless — any user can exploit this passively just by depositing at a favorable time.
- No special privileges, front-running, or external compromise is required.

**Likelihood: High.**

---

### Recommendation

Before computing `rsethAmountToMint`, refresh `rsETHPrice` by calling `_updateRsETHPrice()` (or an equivalent internal update) within `_beforeDeposit`. This ensures the denominator reflects the same asset prices as the numerator, eliminating the stale-price mismatch. Alternatively, compute the mint amount entirely from live prices without relying on the cached `rsETHPrice` state variable.

---

### Proof of Concept

**Setup:**
- Protocol holds 100 stETH; `rsethSupply = 100`; `rsETHPrice = 1.050` (set when stETH/ETH = 1.050)
- stETH/ETH Chainlink feed now returns 1.060 (staking rewards accrued); `updateRSETHPrice()` has not been called yet

**Attack (passive deposit):**
1. Alice calls `depositAsset(stETH, 10e18, 0, "")`
2. `getRsETHAmountToMint` computes: `10e18 × 1.060e18 / 1.050e18 = 10.0952e18` rsETH
3. Alice receives **10.0952 rsETH** instead of the fair **~10.0 rsETH**

**After deposit:**
- Protocol holds 110 stETH; `rsethSupply = 110.0952`
- When `updateRSETHPrice()` is called: `newRsETHPrice = 110 × 1.060 / 110.0952 ≈ 1.05908`
- Existing holders' 100 rsETH is worth `100 × 1.05908 = 105.908 ETH`
- Fair value should be `100 × (110 × 1.060 / 110) = 106.0 ETH`
- **Existing holders lost ~0.092 ETH** of yield to Alice's deposit

The magnitude scales with: (time since last oracle update) × (LST yield rate) × (deposit size). For a large depositor timing their deposit just before a keeper update, the gain is maximized.

### Citations

**File:** contracts/LRTDepositPool.sol (L99-118)
```text
    function depositAsset(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedERC20Token(asset)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(asset, depositAmount, minRSETHAmountExpected);

        // interactions
        IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
        _mintRsETH(rsethAmountToMint);

        emit AssetDeposit(msg.sender, asset, depositAmount, rsethAmountToMint, referralId);
    }
```

**File:** contracts/LRTDepositPool.sol (L519-520)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

**File:** contracts/LRTDepositPool.sol (L648-670)
```text
    function _beforeDeposit(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected
    )
        private
        view
        returns (uint256 rsethAmountToMint)
    {
        if (depositAmount == 0 || depositAmount < minAmountToDeposit) {
            revert InvalidAmountToDeposit();
        }

        if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
            revert MaximumDepositLimitReached();
        }

        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
    }
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L156-158)
```text
    function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
        return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
    }
```

**File:** contracts/LRTOracle.sol (L231-250)
```text
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
