### Title
Unprivileged Token Transfer Permanently Bricks `removeSupportedToken` - (File: contracts/pools/RSETHPool.sol)

### Summary
The `removeSupportedToken` function in `RSETHPool` (and identically in `RSETHPoolNoWrapper`, `RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, and `RSETHPoolV3WithNativeChainBridge`) requires the contract's balance of the token to be exactly zero before removal. Any unprivileged user can transfer a dust amount of a supported token directly to the pool contract, causing this check to permanently revert and preventing the TIMELOCK from ever removing that token from the supported list.

### Finding Description
In `RSETHPool.removeSupportedToken`, line 663 enforces:

```solidity
if (IERC20(token).balanceOf(address(this)) != 0) revert TokenBalanceNotZero();
``` [1](#0-0) 

This check uses the raw `balanceOf` of the contract, which includes any tokens sent directly to the contract outside of the normal deposit/fee flow. Because ERC-20 `transfer` is permissionless, any external account can send 1 wei of a supported token to the pool at any time. Once that happens, `removeSupportedToken` reverts with `TokenBalanceNotZero` for that token.

The same identical guard exists across all five pool variants confirmed by grep: [2](#0-1) [3](#0-2) 

In `RSETHPool`, the BRIDGER_ROLE can drain the non-fee token balance via `moveAssetsForBridging(token, amount)`, but the attacker can front-run the subsequent `removeSupportedToken` call with another 1-wei transfer, making removal practically impossible without atomic execution. In `RSETHPoolV3ExternalBridge`, the `moveAssetsForBridging()` function is explicitly deprecated and reverts, leaving no on-chain path to drain a directly-transferred token balance at all. [4](#0-3) 

### Impact Explanation
**Low — Contract fails to deliver promised returns, but doesn't lose value.**

The TIMELOCK_ROLE permanently loses the ability to remove a supported token from the pool. If that token later becomes deprecated, exploited, or needs to be replaced, the protocol cannot delist it. Users who continue depositing that token receive rsETH priced against a potentially broken oracle or a token with degraded liquidity, but no direct fund theft occurs from this root cause alone.

### Likelihood Explanation
**Medium.** The attack requires only a single permissionless ERC-20 `transfer` of 1 wei to the pool address. No capital is at risk for the attacker (dust cost). The attacker can monitor the mempool and re-execute the transfer whenever the bridger drains the balance, making the griefing sustainable indefinitely at negligible cost.

### Recommendation
Replace the absolute balance check with a delta-based check, or track "externally donated" tokens separately. The simplest fix mirrors the resolution in the referenced Ion-Protocol PR: remove the `balanceOf != 0` guard entirely, or replace it with a check that only the protocol-tracked balance (deposits + fees) is zero:

```solidity
// Instead of:
if (IERC20(token).balanceOf(address(this)) != 0) revert TokenBalanceNotZero();

// Use:
if (feeEarnedInToken[token] != 0) revert TokenBalanceNotZero();
// and separately ensure getTokenBalanceMinusFees(token) == 0
```

Alternatively, add a permissioned `rescueToken` function that allows the admin to sweep any token balance before removal, similar to `SonicChainNativeTokenBridge.recoverTokens`. [5](#0-4) 

### Proof of Concept

1. A supported token (e.g., wstETH) is registered in `RSETHPool` via `addSupportedToken`.
2. Attacker calls `IERC20(wstETH).transfer(address(rsETHPool), 1)` — costs ~1 wei of wstETH.
3. `IERC20(wstETH).balanceOf(address(rsETHPool))` is now `1`.
4. TIMELOCK calls `removeSupportedToken(wstETH, index)`.
5. Execution hits `if (IERC20(token).balanceOf(address(this)) != 0) revert TokenBalanceNotZero()` — reverts.
6. BRIDGER calls `moveAssetsForBridging(wstETH, 1)` to drain the 1 wei.
7. Attacker front-runs the next `removeSupportedToken` call with another `transfer(address(rsETHPool), 1)`.
8. Step 5 repeats indefinitely. In `RSETHPoolV3ExternalBridge`, step 6 is impossible because `moveAssetsForBridging` is deprecated, making the block permanent after a single transfer. [6](#0-5) [7](#0-6)

### Citations

**File:** contracts/pools/RSETHPool.sol (L396-398)
```text
    function getTokenBalanceMinusFees(address token) public view returns (uint256) {
        return IERC20(token).balanceOf(address(this)) - feeEarnedInToken[token];
    }
```

**File:** contracts/pools/RSETHPool.sol (L460-478)
```text
    function moveAssetsForBridging(
        address token,
        uint256 amount
    )
        external
        nonReentrant
        onlySupportedToken(token)
        onlyRole(BRIDGER_ROLE)
    {
        if (amount == 0) revert InvalidAmount();

        // withdraw up to token - fees
        uint256 tokenBalanceMinusFees = getTokenBalanceMinusFees(token);
        if (amount > tokenBalanceMinusFees) revert InsufficientBalanceInPool();

        IERC20(token).safeTransfer(msg.sender, amount);

        emit AssetsMovedForBridging(amount, token);
    }
```

**File:** contracts/pools/RSETHPool.sol (L660-670)
```text
    function removeSupportedToken(address token, uint256 tokenIndex) external onlyRole(TIMELOCK_ROLE) {
        UtilLib.checkNonZeroAddress(token);
        if (supportedTokenList[tokenIndex] != token) revert TokenNotFoundError();
        if (IERC20(token).balanceOf(address(this)) != 0) revert TokenBalanceNotZero();

        delete supportedTokenOracle[token];
        delete tokenBridge[token];
        supportedTokenList[tokenIndex] = supportedTokenList[supportedTokenList.length - 1];
        supportedTokenList.pop();
        emit RemovedSupportedToken(token);
    }
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L1-30)
```text
// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.27;

import { AccessControlUpgradeable } from "@openzeppelin/contracts-upgradeable/access/AccessControlUpgradeable.sol";
import { PausableUpgradeable } from "@openzeppelin/contracts-upgradeable/security/PausableUpgradeable.sol";
import {
    ReentrancyGuardUpgradeable
} from "@openzeppelin/contracts-upgradeable/security/ReentrancyGuardUpgradeable.sol";
import { SafeERC20, IERC20 } from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

import { UtilLib } from "contracts/utils/UtilLib.sol";
import {
    IStargatePoolNative,
    SendParam,
    MessagingFee,
    OFTReceipt,
    MessagingReceipt,
    TxReceipt
} from "contracts/external/layerzero/interfaces/IStargatePoolNative.sol";
import { IL2Messenger } from "contracts/interfaces/L2/IL2Messenger.sol";
import { IL2TokenBridge } from "contracts/interfaces/L2/IL2TokenBridge.sol";

interface IOracle {
    function getRate() external view returns (uint256);
}

/// @title RSETHPoolNoWrapper
/// @notice This contract is the deposit pool for the chains where there is no rsETH wrapper contract (e.g. Arbitrum,
/// Unichain)
contract RSETHPoolNoWrapper is AccessControlUpgradeable, PausableUpgradeable, ReentrancyGuardUpgradeable {
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L640-648)
```text
        IERC20(token).safeTransfer(receiver, amountToSendInToken);

        emit FeesWithdrawn(amountToSendInToken, token);
    }

    /// @dev Legacy function - Withdraws assets from the contract for bridging
    function moveAssetsForBridging() external view onlyRole(BRIDGER_ROLE) {
        revert DeprecatedFunction();
    }
```

**File:** contracts/bridges/SonicChainNativeTokenBridge.sol (L160-173)
```text
    function recoverTokens(
        address tokenAddress,
        address recipient,
        uint256 amount
    )
        external
        onlyRole(DEFAULT_ADMIN_ROLE)
    {
        UtilLib.checkNonZeroAddress(tokenAddress);
        UtilLib.checkNonZeroAddress(recipient);
        if (amount == 0) revert InvalidAmount();

        IERC20(tokenAddress).safeTransfer(recipient, amount);
    }
```
