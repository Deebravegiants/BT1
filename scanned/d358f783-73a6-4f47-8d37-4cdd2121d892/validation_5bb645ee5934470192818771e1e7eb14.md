### Title
Griefing DoS on `removeSupportedToken` via Dust Token Transfer - (File: `contracts/pools/RSETHPoolV3.sol`, `contracts/pools/RSETHPoolV3ExternalBridge.sol`)

### Summary

The `removeSupportedToken` function in both `RSETHPoolV3` and `RSETHPoolV3ExternalBridge` guards removal with a strict zero-balance check on the pool's own token balance. Any unprivileged actor can send 1 wei of a supported token directly to the pool contract, causing this check to permanently revert and blocking the `TIMELOCK_ROLE` from ever removing that token from the supported list.

### Finding Description

Both pool contracts implement `removeSupportedToken` with the following guard:

```solidity
// RSETHPoolV3.sol line 562
if (IERC20(token).balanceOf(address(this)) != 0) revert TokenBalanceNotZero();
```

```solidity
// RSETHPoolV3ExternalBridge.sol line 772
if (IERC20(token).balanceOf(address(this)) != 0) revert TokenBalanceNotZero();
``` [1](#0-0) [2](#0-1) 

The pool contract addresses are fixed and publicly known. Any ERC-20 token that implements a permissionless `transfer` allows any holder to send 1 wei directly to the pool. Because the check is `!= 0` (not `> someNegligibleThreshold`), even a single wei donation permanently blocks removal. The attacker does not need to front-run anything — the pool address is already deployed and known.

The attack path:
1. Observe that token `T` is a supported token in the pool.
2. Transfer 1 wei of `T` directly to the pool contract address.
3. Any subsequent call to `removeSupportedToken(T, index)` by `TIMELOCK_ROLE` reverts with `TokenBalanceNotZero`.

Cost: 1 wei of the target token plus gas.

### Impact Explanation

`removeSupportedToken` is the protocol's safety valve for retiring a token that has become deprecated, compromised, or otherwise undesirable. If this function is permanently blocked:

- The protocol cannot delist a token whose oracle becomes stale or manipulable.
- The protocol cannot delist a token that has been exploited or paused at the token level.
- Users continue to be able to deposit that token and receive `wrsETH`, potentially at an incorrect rate.
- The only remaining mitigation is pausing the **entire** pool contract, which also blocks all legitimate deposits and bridging operations — a much heavier-handed response.

This maps to **Low — contract fails to deliver promised returns** (the promised ability to safely manage the supported token list is broken), with a realistic path to **Medium — temporary freezing of funds** if the compromised token's oracle diverges and users deposit against it before the admin can pause.

### Likelihood Explanation

- The attacker needs only to hold 1 wei of any supported token (e.g., wstETH, which is freely tradeable).
- No privileged access, no front-running, no complex setup is required.
- The pool contract address is publicly known and immutable.
- The attack is cheap, repeatable, and can be applied to every supported token simultaneously.

### Recommendation

Replace the strict zero-balance check with a threshold-based check, consistent with the pattern already used in `LRTDepositPool._checkResidueLSTBalance` and `_checkResidueEthBalance`, which compare against `maxNegligibleAmount`:

```solidity
// Instead of:
if (IERC20(token).balanceOf(address(this)) != 0) revert TokenBalanceNotZero();

// Use:
if (IERC20(token).balanceOf(address(this)) > maxNegligibleAmount) revert TokenBalanceNotZero();
``` [3](#0-2) 

Alternatively, allow the admin to sweep dust amounts of a token before removal, or allow removal when the only balance present is below a configurable dust threshold.

### Proof of Concept

```solidity
// Attacker holds 1 wei of wstETH (a supported token in RSETHPoolV3ExternalBridge)
IERC20(wstETH).transfer(address(pool), 1);

// Now TIMELOCK_ROLE can never call:
pool.removeSupportedToken(wstETH, tokenIndex);
// => reverts with TokenBalanceNotZero()
```

The `removeSupportedToken` function in `RSETHPoolV3.sol` at line 562 and in `RSETHPoolV3ExternalBridge.sol` at line 772 both contain the identical vulnerable check. [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L559-568)
```text
    function removeSupportedToken(address token, uint256 tokenIndex) external onlyRole(TIMELOCK_ROLE) {
        UtilLib.checkNonZeroAddress(token);
        if (supportedTokenList[tokenIndex] != token) revert TokenNotFoundError();
        if (IERC20(token).balanceOf(address(this)) != 0) revert TokenBalanceNotZero();

        delete supportedTokenOracle[token];
        supportedTokenList[tokenIndex] = supportedTokenList[supportedTokenList.length - 1];
        supportedTokenList.pop();
        emit RemovedSupportedToken(token);
    }
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L769-779)
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

**File:** contracts/LRTDepositPool.sol (L627-645)
```text
    function _checkResidueLSTBalance(address nodeDelegatorAddress) internal view {
        address[] memory supportedAssets = lrtConfig.getSupportedAssetList();
        uint256 supportedAssetsLength = supportedAssets.length;

        uint256 assetBalance;
        for (uint256 i; i < supportedAssetsLength; ++i) {
            if (supportedAssets[i] == LRTConstants.ETH_TOKEN) {
                // this function only checks for residual LST balance
                continue;
            }

            assetBalance = IERC20(supportedAssets[i]).balanceOf(nodeDelegatorAddress)
                + INodeDelegator(nodeDelegatorAddress).getAssetBalance(supportedAssets[i]);
            assetBalance += INodeDelegator(nodeDelegatorAddress).getAssetUnstaking(supportedAssets[i]);

            if (assetBalance > maxNegligibleAmount) {
                revert NodeDelegatorHasAssetBalance(supportedAssets[i], assetBalance);
            }
        }
```
