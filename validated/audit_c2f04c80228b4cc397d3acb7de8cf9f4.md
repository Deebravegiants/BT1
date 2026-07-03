### Title
First Depositor Inflation Attack via `getRsETHAmountToMint` Rounding to Zero — (`contracts/LRTDepositPool.sol`)

---

### Summary

An unprivileged first depositor can inflate the `rsETHPrice` by donating ETH directly to `LRTDepositPool` and calling the public `updateRSETHPrice()`. This causes the integer division in `getRsETHAmountToMint` to round to zero for subsequent depositors who pass `minRSETHAmountExpected = 0`. Those depositors transfer ETH into the pool but receive 0 rsETH, permanently losing their funds to the attacker's inflated rsETH position.

---

### Finding Description

`getRsETHAmountToMint` computes the rsETH to mint as:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

This is a plain integer division. When `amount * assetPrice < rsETHPrice`, the result truncates to zero. [1](#0-0) 

The slippage guard in `_beforeDeposit` only reverts when `rsethAmountToMint < minRSETHAmountExpected`. If the caller passes `minRSETHAmountExpected = 0` (the natural default), the condition `0 < 0` is false and the call proceeds — minting 0 rsETH while consuming the full deposit. [2](#0-1) 

The rsETH price is computed in `_updateRsETHPrice` as:

```solidity
uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
``` [3](#0-2) 

`totalETHInProtocol` is built by `_getTotalEthInProtocol`, which calls `getTotalAssetDeposits(ETH)`, which in turn reads `address(this).balance` of the deposit pool as `ethLyingInDepositPool`. [4](#0-3) [5](#0-4) 

`LRTDepositPool` has an open `receive()` function, so any address can donate ETH to it without minting rsETH, directly inflating the numerator of the price formula. [6](#0-5) 

`updateRSETHPrice()` is a public, permissionless function — anyone can trigger the price update after the donation. [7](#0-6) 

---

### Impact Explanation

**Critical — Direct theft of user funds.**

After the attacker inflates `rsETHPrice` to `(1 + D) * 1e18` (where D is the donated ETH), any victim depositing `V < (1 + D)` ETH receives 0 rsETH. The victim's ETH is permanently absorbed into the pool and backs the attacker's single-wei rsETH position. When the attacker later redeems, they recover their donation plus the victim's ETH. The victim has no recourse because 0 rsETH was minted to them.

---

### Likelihood Explanation

**Medium.** The attack requires the attacker to:
1. Be the first (or very early) depositor to hold a small rsETH position.
2. Donate a large amount of ETH to the pool — a capital cost that is fully recoverable upon withdrawal.
3. Front-run or wait for a victim who calls `depositETH` with `minRSETHAmountExpected = 0`.

The `minRSETHAmountExpected = 0` default is the natural value for any integrator, script, or user who does not explicitly compute and pass a slippage bound. `updateRSETHPrice()` is public and can be called by the attacker immediately after the donation. The attack is economically rational: the attacker's donated ETH is not lost — it is recovered at withdrawal along with the victim's ETH.

---

### Recommendation

1. **Reject zero-rsETH mints**: In `_beforeDeposit`, add `require(rsethAmountToMint > 0, "zero rsETH minted")` unconditionally, analogous to the `MINIMUM_K` fix in the referenced report.

2. **Enforce a minimum rsETH mint amount**: Set a protocol-level `MINIMUM_RSETH_MINT` constant (e.g., `1e9`) and revert if `rsethAmountToMint < MINIMUM_RSETH_MINT`.

3. **Restrict direct ETH donations**: Consider removing or restricting the open `receive()` function, or excluding unaccounted ETH balance from `totalETHInProtocol` (e.g., only count ETH that entered via `depositETH`).

4. **Document the slippage parameter**: Clearly require callers to pass a non-zero `minRSETHAmountExpected` and consider reverting when it is zero.

---

### Proof of Concept

```solidity
// Attacker steps:

// 1. Deposit 1 wei ETH — gets 1 wei rsETH at initial price 1e18
lrtDepositPool.depositETH{value: 1}(0, "");

// 2. Donate 1000 ETH directly to the pool (no rsETH minted)
(bool ok,) = address(lrtDepositPool).call{value: 1000 ether}("");

// 3. Trigger price update — rsETHPrice becomes ~1001e18
lrtOracle.updateRSETHPrice();

// 4. Victim deposits 999 ETH with default minRSETHAmountExpected = 0
//    rsethAmountToMint = 999e18 * 1e18 / 1001e18 = 0  (rounds down)
//    Victim receives 0 rsETH; 999 ETH absorbed into pool
lrtDepositPool.depositETH{value: 999 ether}(0, ""); // victim tx

// 5. Attacker's 1 wei rsETH is now backed by 2000 ETH
//    Attacker requests withdrawal → recovers ~2000 ETH
//    Net profit: ~999 ETH (victim's full deposit)
```

The root cause — `(amount * assetPrice) / rsETHPrice` truncating to zero — is the direct analog of `(_x * _y) / 1e18 = 0` in the Velodrome stable pool invariant. Both allow the first liquidity provider to absorb subsequent depositors' funds through a rounding-to-zero exploit. [8](#0-7) [9](#0-8) [10](#0-9)

### Citations

**File:** contracts/LRTDepositPool.sol (L58-58)
```text
    receive() external payable { }
```

**File:** contracts/LRTDepositPool.sol (L480-480)
```text
        ethLyingInDepositPool = address(this).balance;
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

**File:** contracts/LRTOracle.sol (L331-343)
```text
    function _getTotalEthInProtocol() private view returns (uint256 totalETHInProtocol) {
        address lrtDepositPoolAddr = lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL);
        address[] memory supportedAssets = lrtConfig.getSupportedAssetList();
        uint256 supportedAssetCount = supportedAssets.length;

        for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
            address asset = supportedAssets[assetIdx];
            // assetER is in 1e18 precision (1.0 = 1e18)
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);
```
