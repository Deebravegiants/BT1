### Title
Permanent Freezing of Bridger-Deposited altAgETH Collateral After `removeAllowedToken` — (`contracts/agETH/AGETHTokenWrapper.sol`)

### Summary

`AGETHTokenWrapper` allows `DEFAULT_ADMIN_ROLE` to call `removeAllowedToken`, which permanently disables withdrawals for that token. Because the contract has **no `addAllowedToken` function** (explicitly omitted by design) and **no `recoverTokens` function**, any altAgETH deposited by the bridger via `depositBridgerAssets` becomes permanently unrecoverable after the token is removed.

### Finding Description

The contract exposes two relevant functions:

**`depositBridgerAssets`** — callable by `BRIDGER_ROLE`, deposits altAgETH as collateral for already-minted wrapper tokens without minting new ones: [1](#0-0) 

**`removeAllowedToken`** — callable by `DEFAULT_ADMIN_ROLE`, sets `allowedTokens[_asset] = false` with no preconditions (no balance check, no supply check): [2](#0-1) 

**`_withdraw`** — hard-reverts with `TokenNotAllowed` if the asset is not in `allowedTokens`: [3](#0-2) 

The comment at line 153 explicitly confirms there is no re-add path: [4](#0-3) 

This contrasts directly with `RsETHTokenWrapper`, which has a public `addAllowedToken` function and gates removal behind `TIMELOCK_ROLE`: [5](#0-4) 

### Impact Explanation

After the sequence:
1. `depositBridgerAssets(altAgETH, X)` — X altAgETH enters the contract as collateral
2. `removeAllowedToken(altAgETH)` — token disabled, no re-enable path exists
3. `withdraw(altAgETH, X)` — reverts unconditionally with `TokenNotAllowed`

The X altAgETH (including all accrued yield) is permanently locked in the contract with zero recovery path. This satisfies **Medium: Permanent freezing of unclaimed yield** (the yield accrued on the locked altAgETH is irrecoverable), and arguably **Critical: Permanent freezing of funds** (the principal collateral itself is frozen).

### Likelihood Explanation

This does **not** require admin key compromise or malicious intent. A legitimate operational reason to call `removeAllowedToken` (e.g., deprecating a bridge, replacing a faulty altAgETH token) would trigger the freeze as a side effect. The missing precondition check (no guard against `balanceOf(altAgETH) > 0` before removal) makes this reachable through normal admin operations.

### Recommendation

1. Add a balance guard to `removeAllowedToken` — revert if `ERC20(asset).balanceOf(address(this)) > 0`.
2. Add an `addAllowedToken` function (mirroring `RsETHTokenWrapper`) so a removed token can be re-enabled.
3. Add a `recoverTokens` emergency function restricted to a timelock, allowing recovery only of tokens with zero outstanding wrapper supply.

### Proof of Concept

```solidity
// 1. Bridger deposits X altAgETH as collateral
wrapper.depositBridgerAssets(altAgETH, X);
assert(IERC20(altAgETH).balanceOf(address(wrapper)) == X);

// 2. Admin removes the token (legitimate deprecation scenario)
wrapper.removeAllowedToken(altAgETH);
assert(wrapper.allowedTokens(altAgETH) == false);

// 3. Wrapper token holder attempts to redeem — reverts
vm.expectRevert(AGETHTokenWrapper.TokenNotAllowed.selector);
wrapper.withdraw(altAgETH, X);

// 4. No recovery path exists — funds permanently frozen
// addAllowedToken does not exist; recoverTokens does not exist
assert(IERC20(altAgETH).balanceOf(address(wrapper)) == X); // still locked
```

### Citations

**File:** contracts/agETH/AGETHTokenWrapper.sol (L111-113)
```text
    function _withdraw(address _asset, address _to, uint256 _amount) internal {
        if (!allowedTokens[_asset]) revert TokenNotAllowed();

```

**File:** contracts/agETH/AGETHTokenWrapper.sol (L143-151)
```text
    function depositBridgerAssets(address _asset, uint256 _amount) external onlyRole(BRIDGER_ROLE) {
        if (maxAmountToDepositBridgerAsset(_asset) < _amount) {
            revert CannotDeposit();
        }

        ERC20Upgradeable(_asset).safeTransferFrom(msg.sender, address(this), _amount);

        emit BridgerDeposited(_asset, _amount);
    }
```

**File:** contracts/agETH/AGETHTokenWrapper.sol (L153-153)
```text
    /// Dont' allow to add other tokens at the moment. Only allow the altAgETH token as set in the initialize function
```

**File:** contracts/agETH/AGETHTokenWrapper.sol (L157-160)
```text
    function removeAllowedToken(address _asset) external onlyRole(DEFAULT_ADMIN_ROLE) {
        allowedTokens[_asset] = false;
        emit TokenRemoved(_asset);
    }
```

**File:** contracts/L2/RsETHTokenWrapper.sol (L174-185)
```text
    function addAllowedToken(address _asset) external onlyRole(TIMELOCK_ROLE) {
        _addAllowedToken(_asset);
    }

    /// @dev Remove a token from the allowed tokens list
    /// @param _asset The address of the token to remove
    function removeAllowedToken(address _asset) external onlyRole(TIMELOCK_ROLE) {
        if (!allowedTokens[_asset]) revert TokenNotAllowed();

        allowedTokens[_asset] = false;
        emit TokenRemoved(_asset);
    }
```
