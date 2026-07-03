### Title
Donation-Based rsETH Price Inflation Attack via `LRTDepositPool.receive()` — (`contracts/LRTDepositPool.sol` / `contracts/LRTOracle.sol`)

---

### Summary

An attacker who is the first (or sole) depositor in `LRTDepositPool` can donate ETH directly to the contract, then call the public `updateRSETHPrice()` to inflate the stored `rsETHPrice`. Subsequent depositors who pass `minRSETHAmountExpected = 0` receive 0 rsETH and permanently lose their deposited ETH, which the attacker can later reclaim through the withdrawal mechanism.

---

### Finding Description

**Step 1 — Attacker becomes first depositor.**
`LRTDepositPool.depositETH` mints rsETH using the formula:

```
rsethAmountToMint = (amount * assetPrice) / rsETHPrice
```

When `rsethSupply == 0`, `_updateRsETHPrice` hard-codes `rsETHPrice = 1e18`. The attacker deposits 1 wei of ETH and receives 1 wei of rsETH. [1](#0-0) 

**Step 2 — Attacker donates ETH to inflate `totalETHInProtocol`.**
`LRTDepositPool` has an unrestricted `receive()` function:

```solidity
receive() external payable { }
``` [2](#0-1) 

`getETHDistributionData()` counts the raw ETH balance of the contract as protocol-owned ETH:

```solidity
ethLyingInDepositPool = address(this).balance;
``` [3](#0-2) 

Any ETH sent directly to the contract is therefore included in `_getTotalEthInProtocol()`, which feeds the price calculation. [4](#0-3) 

**Step 3 — Attacker calls `updateRSETHPrice()` to commit the inflated price.**
`updateRSETHPrice()` is publicly callable with no access restriction:

```solidity
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
``` [5](#0-4) 

The new price is computed as:

```solidity
uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
``` [6](#0-5) 

With `rsethSupply = 1 wei` and `totalETHInProtocol = 1 + X` (where X is the donated amount), `rsETHPrice` becomes `(1 + X) * 1e18`.

The only guard against a large price jump is `pricePercentageLimit`, but this variable is **never set in `initialize`** and therefore defaults to `0`, making the check a no-op:

```solidity
bool isPriceIncreaseOffLimit =
    pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);
``` [7](#0-6) 

**Step 4 — Victim deposits with `minRSETHAmountExpected = 0`.**
`_beforeDeposit` only reverts if `rsethAmountToMint < minRSETHAmountExpected`. When the victim passes `0`, the check is trivially satisfied even if `rsethAmountToMint == 0`:

```solidity
rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);
if (rsethAmountToMint < minRSETHAmountExpected) {
    revert MinimumAmountToReceiveNotMet();
}
``` [8](#0-7) 

With `rsETHPrice = (1 + X) * 1e18`, a victim depositing `Y < 1 + X` ETH receives:

```
rsethAmountToMint = Y * 1e18 / ((1 + X) * 1e18) = Y / (1 + X) → 0 (rounds down)
```

The victim's ETH is accepted, 0 rsETH is minted, and `_mintRsETH(0)` executes silently. [9](#0-8) 

**Step 5 — Attacker withdraws all funds.**
The attacker holds the only 1 wei of rsETH in existence. The protocol's total ETH is now `1 + X + Y`. When the attacker redeems their rsETH through the withdrawal mechanism, they recover `1 + X + Y` ETH — their original deposit, their donation, and the victim's deposit — for a net profit of `Y - 1 wei`.

---

### Impact Explanation

**Critical — direct theft of user funds.** Any depositor who calls `depositETH` or `depositAsset` with `minRSETHAmountExpected = 0` after the price has been inflated loses 100% of their deposit. The attacker recovers the full protocol balance including all stolen deposits.

---

### Likelihood Explanation

**Medium.** The attack requires:
1. The attacker to be the first (or only) depositor — achievable at protocol launch or after a period of zero deposits.
2. `pricePercentageLimit == 0` — this is the **default** state since `initialize` never sets it.
3. A victim to call `depositETH`/`depositAsset` with `minRSETHAmountExpected = 0` — common in practice and in integrations that omit slippage protection.
4. The attacker to commit capital ≈ the victim's deposit size (standard inflation-attack cost).

No front-running is required; the attacker can inflate the price and wait for victims.

---

### Recommendation

1. **Enforce a minimum rsETH output.** Revert in `_beforeDeposit` (or `_mintRsETH`) if `rsethAmountToMint == 0`:
   ```solidity
   if (rsethAmountToMint == 0) revert ZeroRsETHMinted();
   ```
2. **Set `pricePercentageLimit` to a non-zero value during `initialize`** (e.g., 1% = `1e16`) so that a single large donation cannot inflate the price in one transaction.
3. **Track deposited ETH separately from raw balance.** Replace `address(this).balance` in `getETHDistributionData` with an internal accounting variable that is only incremented on legitimate deposits, preventing untracked donations from affecting the price.

---

### Proof of Concept

```
1. Deploy protocol; rsETHPrice = 1e18, rsethSupply = 0.
2. Attacker calls depositETH{value: 1}(0, "") → receives 1 wei rsETH.
3. Attacker sends 15e18 ETH directly to LRTDepositPool (via receive()).
4. Attacker calls lrtOracle.updateRSETHPrice().
   → rsETHPrice = (1 + 15e18) * 1e18 / 1 ≈ 15e36
5. Victim calls depositETH{value: 10e18}(0, "").
   → rsethAmountToMint = 10e18 * 1e18 / 15e36 = 0
   → Victim receives 0 rsETH; 10e18 ETH is now in the protocol.
6. Attacker initiates withdrawal of 1 wei rsETH.
   → Attacker recovers ≈ 25e18 + 1 ETH (their donation + victim's deposit).
   → Net profit ≈ 10e18 ETH.
``` [10](#0-9) [11](#0-10)

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

**File:** contracts/LRTOracle.sol (L256-257)
```text
            bool isPriceIncreaseOffLimit =
                pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);
```

**File:** contracts/LRTOracle.sol (L331-349)
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

            unchecked {
                ++assetIdx;
            }
        }
    }
```

**File:** contracts/LRTDepositPool.sol (L58-58)
```text
    receive() external payable { }
```

**File:** contracts/LRTDepositPool.sol (L76-93)
```text
    function depositETH(
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        payable
        nonReentrant
        whenNotPaused
        onlySupportedAsset(LRTConstants.ETH_TOKEN)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);

        // interactions
        _mintRsETH(rsethAmountToMint);

        emit ETHDeposit(msg.sender, msg.value, rsethAmountToMint, referralId);
    }
```

**File:** contracts/LRTDepositPool.sol (L480-480)
```text
        ethLyingInDepositPool = address(this).balance;
```

**File:** contracts/LRTDepositPool.sol (L665-669)
```text
        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
```

**File:** contracts/LRTDepositPool.sol (L686-690)
```text
    function _mintRsETH(uint256 rsethAmountToMint) private {
        address rsethToken = lrtConfig.rsETH();
        // mint rseth for user
        IRSETH(rsethToken).mint(msg.sender, rsethAmountToMint);
    }
```
