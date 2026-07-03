### Title
Token Deposit Fees Incorrectly Credited to `feeEarnedInETH`, Permanently Blocking ETH Bridging - (File: contracts/pools/RSETHPoolNoWrapper.sol)

### Summary

In `RSETHPoolNoWrapper`, the ERC20 token deposit path adds the collected fee to `feeEarnedInETH` instead of `feeEarnedInToken[token]`. Because `feeEarnedInETH` is denominated in wei and is subtracted from the contract's native ETH balance in `getETHBalanceMinusFees()`, inflating it with token-unit fee amounts causes that function to revert with an arithmetic underflow. Both `bridgeAssets` and `bridgeAssetsViaNativeBridge` depend on `getETHBalanceMinusFees()`, so once the inflation exceeds the ETH balance, all ETH bridging to L1 is permanently blocked and the ETH deposited by users is frozen in the L2 pool.

### Finding Description

`RSETHPoolNoWrapper.deposit(address token, uint256 amount, string referralId)` computes a fee in token units and then writes it to the wrong state variable:

```solidity
// contracts/pools/RSETHPoolNoWrapper.sol  lines 260-271
(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

feeEarnedInETH += fee;          // ← BUG: fee is in token units, not ETH

rsETH.safeTransfer(msg.sender, rsETHAmount);
```

The sibling contract `RSETHPoolV3` performs the same operation correctly:

```solidity
// contracts/pools/RSETHPoolV3.sol  lines 286-290
(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

feeEarnedInToken[token] += fee;  // ← correct
```

`getETHBalanceMinusFees()` performs an unchecked subtraction in Solidity 0.8, which reverts on underflow:

```solidity
// contracts/pools/RSETHPoolNoWrapper.sol  lines 352-354
function getETHBalanceMinusFees() public view returns (uint256) {
    return address(this).balance - feeEarnedInETH;
}
```

Both bridging paths call this function:

```solidity
// contracts/pools/RSETHPoolNoWrapper.sol  line 461
if (getETHBalanceMinusFees() - msg.value < amount) { revert InsufficientETHBalance(); }

// contracts/pools/RSETHPoolNoWrapper.sol  line 437
uint256 ethBalanceMinusFees = getETHBalanceMinusFees();
IL2Messenger(messenger).sendETHToL1ViaBridge{ value: ethBalanceMinusFees }(...);
```

There is no admin function to reset `feeEarnedInETH` independently of sending ETH, and `withdrawFees(address receiver)` also reverts when `feeEarnedInETH > address(this).balance`, so the inflated value cannot be corrected without a contract upgrade.

### Impact Explanation

Once cumulative token-deposit fees (in token units) exceed the pool's native ETH balance, `getETHBalanceMinusFees()` reverts permanently. This blocks `bridgeAssets` and `bridgeAssetsViaNativeBridge`, trapping all ETH deposited by users inside the L2 pool. The ETH cannot reach `L1Vault` → `LRTDepositPool` → EigenLayer, so it earns no restaking yield and is effectively frozen until a contract upgrade is deployed. This matches the **Medium: Temporary freezing of funds** impact tier.

### Likelihood Explanation

The trigger is the public `deposit(address token, uint256 amount, string referralId)` function, callable by any user with no role requirement. On Arbitrum or Unichain deployments where stETH or similar LSTs are supported tokens, a single large token deposit (or many small ones) is sufficient to inflate `feeEarnedInETH` past the ETH balance, especially if ETH deposits are sparse. No privileged access, front-running, or external dependency failure is required.

### Recommendation

Change the token deposit path to credit the correct mapping:

```solidity
// contracts/pools/RSETHPoolNoWrapper.sol
- feeEarnedInETH += fee;
+ feeEarnedInToken[token] += fee;
```

This mirrors the correct implementation already present in `RSETHPoolV3`.

### Proof of Concept

1. Pool is deployed on Arbitrum with stETH as a supported token; `feeBps = 50`; ETH balance = 0 (no ETH deposits yet).
2. Alice calls `deposit(stETH, 1_000e18, "")`.
   - `fee = 1_000e18 * 50 / 10_000 = 5e18` (5 stETH in token units).
   - `feeEarnedInETH += 5e18` → `feeEarnedInETH = 5e18`.
3. `address(this).balance = 0` (no ETH was received).
4. Bridger calls `bridgeAssets(amount, minAmount, nativeFee)`.
   - Internally calls `getETHBalanceMinusFees()` → `0 - 5e18` → arithmetic underflow → **revert**.
5. Bridger calls `bridgeAssetsViaNativeBridge()`.
   - Same path → **revert**.
6. Bridger calls `withdrawFees(receiver)` to try to reset `feeEarnedInETH`.
   - Attempts `payable(receiver).call{value: 5e18}("")` with 0 ETH balance → **revert**.
7. All ETH subsequently deposited by users is permanently trapped in the pool. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L260-271)
```text
        if (amount == 0) revert InvalidAmount();

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        rsETH.safeTransfer(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId); // Add token address?
    }
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L352-354)
```text
    function getETHBalanceMinusFees() public view returns (uint256) {
        return address(this).balance - feeEarnedInETH;
    }
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L431-443)
```text
    function bridgeAssetsViaNativeBridge() external nonReentrant onlyRole(BRIDGER_ROLE) {
        UtilLib.checkNonZeroAddress(l2Bridge);
        UtilLib.checkNonZeroAddress(messenger);
        UtilLib.checkNonZeroAddress(l1VaultETHForL2Chain);

        // withdraw ETH - fees
        uint256 ethBalanceMinusFees = getETHBalanceMinusFees();

        IL2Messenger(messenger).sendETHToL1ViaBridge{ value: ethBalanceMinusFees }(
            l2Bridge, l1VaultETHForL2Chain, ethBalanceMinusFees
        );

        emit BridgedETHToL1ViaNativeBridge(l1VaultETHForL2Chain, ethBalanceMinusFees);
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L459-463)
```text
    {
        // Exclude msg.value so reserved fees can’t be accidentally consumed
        if (getETHBalanceMinusFees() - msg.value < amount) {
            revert InsufficientETHBalance();
        }
```

**File:** contracts/pools/RSETHPoolV3.sol (L286-292)
```text
        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId, token);
```
