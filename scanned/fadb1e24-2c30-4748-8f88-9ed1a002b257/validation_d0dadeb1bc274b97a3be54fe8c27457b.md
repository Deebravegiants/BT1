### Title
Stale `rsETHPrice` Used in `depositETH`/`depositAsset` Allows Depositors to Mint Excess rsETH - (File: contracts/LRTDepositPool.sol)

---

### Summary

`LRTDepositPool.depositETH()` and `depositAsset()` compute the rsETH mint amount using the cached `LRTOracle.rsETHPrice` without first refreshing it via the public `updateRSETHPrice()`. Because rsETH is a yield-bearing token whose price monotonically increases as staking rewards accrue, any window between oracle updates leaves the cached price stale (lower than actual). A depositor who acts during this window receives more rsETH than their deposit is worth at the current price, stealing accrued yield from existing rsETH holders.

---

### Finding Description

`LRTDepositPool.getRsETHAmountToMint()` divides the deposit value by the cached `rsETHPrice`:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

`rsETHPrice` is a storage variable in `LRTOracle` that is only updated when `updateRSETHPrice()` is explicitly called. That function is **public and permissionless** (subject only to `whenNotPaused`):

```solidity
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
```

Neither `depositETH()` nor `depositAsset()` calls `updateRSETHPrice()` before invoking `_beforeDeposit()` → `getRsETHAmountToMint()`. The full call chain is:

- `depositETH()` → `_beforeDeposit()` → `getRsETHAmountToMint()` → reads `lrtOracle.rsETHPrice()` (cached)
- `depositAsset()` → `_beforeDeposit()` → `getRsETHAmountToMint()` → reads `lrtOracle.rsETHPrice()` (cached)

Between operator-triggered oracle updates, staking rewards cause the true rsETH/ETH ratio to rise above the cached value. Because `rsETHPrice` appears in the denominator, a stale (lower) value inflates `rsethAmountToMint`, minting more rsETH than the depositor's contribution warrants.

The `_updateRsETHPrice()` internal function itself computes the correct price from live on-chain TVL data, so the correct price is always derivable — it is simply never forced before a deposit.

---

### Impact Explanation

**Theft of unclaimed yield (High).**

Every deposit made against a stale `rsETHPrice` mints excess rsETH. This excess dilutes all existing rsETH holders: their proportional claim on the protocol's ETH TVL shrinks without any corresponding reduction in their token balance. The attacker's profit equals the yield accrued since the last `updateRSETHPrice()` call, scaled by their deposit size. With a large deposit and a multi-day staleness window, the stolen yield can be material.

---

### Likelihood Explanation

- `updateRSETHPrice()` is called by the operator on a periodic schedule, not atomically with every deposit. Any gap between calls is exploitable.
- The attack requires no special role — any address that can call `depositETH()` or `depositAsset()` can exploit it.
- The attacker can trivially detect the opportunity by comparing `LRTOracle.rsETHPrice` against the live TVL returned by `LRTDepositPool.getTotalAssetDeposits()` and `IRSETH.totalSupply()`.
- The `pricePercentageLimit` guard in `_updateRsETHPrice()` can actually widen the window: if the price has risen above the daily threshold, only a manager can call `updateRSETHPriceAsManager()`, meaning the stale price persists until the manager acts, giving the attacker more time.

---

### Recommendation

Call `updateRSETHPrice()` (or its internal equivalent) at the start of `depositETH()` and `depositAsset()` in `LRTDepositPool`, mirroring the FraxLend recommendation of forcing an exchange-rate refresh in every function that mints shares against a price-sensitive denominator.

---

### Proof of Concept

1. At time T, the operator calls `updateRSETHPrice()`. `LRTOracle.rsETHPrice` is set to `1.05e18` (1.05 ETH per rsETH).
2. Staking rewards accrue over the next 24 hours. The true price rises to `1.06e18`, but `rsETHPrice` remains `1.05e18`.
3. Alice calls `depositETH{value: 100 ether}(0, "")`.
4. `getRsETHAmountToMint` computes: `100e18 * 1e18 / 1.05e18 ≈ 95.238 rsETH`.
5. The correct amount at the live price would be: `100e18 * 1e18 / 1.06e18 ≈ 94.340 rsETH`.
6. Alice receives **≈ 0.898 rsETH excess**, stealing yield that belongs to existing rsETH holders.
7. Alice (or anyone) then calls `updateRSETHPrice()` to advance the price to `1.06e18`, locking in the dilution.

---

**Root cause references:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

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

**File:** contracts/LRTOracle.sol (L214-251)
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
