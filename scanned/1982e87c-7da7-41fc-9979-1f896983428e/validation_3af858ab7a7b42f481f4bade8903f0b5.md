The vulnerability is real and concrete. Here is the full analysis:

---

### Title
Missing `address(this)` Recipient Guard Allows Permanent Freezing of altRsETH and wrsETH — (`contracts/L2/RsETHTokenWrapper.sol`)

### Summary
`depositTo` passes `_to` directly to `_deposit` with no validation. When `_to == address(this)`, wrsETH is minted to the wrapper contract itself. Because `_withdraw` burns only from `msg.sender` and the wrapper has no self-call mechanism or rescue function, the minted wrsETH — and the corresponding altRsETH collateral — are permanently locked.

### Finding Description

`depositTo` at line 77–79 forwards `_to` to `_deposit` without any guard: [1](#0-0) 

`_deposit` at line 134–141 has no check for `_to == address(this)`: [2](#0-1) 

When `_to` is `address(this)`:
- `safeTransferFrom` moves N altRsETH from the caller into the wrapper (line 137)
- `_mint` credits N wrsETH to the wrapper contract itself (line 139)

`_withdraw` always burns from `msg.sender` (line 123), not from an arbitrary holder: [3](#0-2) 

No external caller can burn the wrapper's own wrsETH balance. The wrapper has no self-initiated `withdraw` path, and `RsETHTokenWrapper` contains no `rescue`, `sweep`, or `recoverTokens` function (unlike other contracts in the repo such as `Recoverable.sol` and `SonicBridgeReceiver`). [4](#0-3) 

Notably, OpenZeppelin's own `ERC20WrapperUpgradeable.depositFor` explicitly prevents this exact scenario with:

```solidity
require(sender != address(this), "ERC20Wrapper: wrapper can't deposit");
``` [5](#0-4) 

`RsETHTokenWrapper` omits this guard entirely.

### Impact Explanation
N altRsETH deposited by the caller is permanently locked inside the wrapper. The N wrsETH minted to the wrapper can never be burned by any party. Because withdrawing altRsETH requires burning wrsETH from `msg.sender`, and the wrapper cannot act as its own `msg.sender` to call `withdraw`, the collateral is irrecoverable. This constitutes permanent freezing of funds.

### Likelihood Explanation
Any caller with an allowed altRsETH token and a non-zero balance can trigger this by passing `address(wrapper)` as `_to`. No special role, privilege, or precondition is required beyond token approval. The call is permissionless and irreversible.

### Recommendation
Add a guard in `_deposit` rejecting `address(this)` as recipient:

```solidity
function _deposit(address _asset, address _to, uint256 _amount) internal {
    if (!allowedTokens[_asset]) revert TokenNotAllowed();
+   if (_to == address(this)) revert InvalidRecipient();
    ERC20Upgradeable(_asset).safeTransferFrom(msg.sender, address(this), _amount);
    _mint(_to, _amount);
    emit Deposit(_asset, msg.sender, _to, _amount);
}
```

This mirrors the guard in OZ's `ERC20WrapperUpgradeable.depositFor`.

### Proof of Concept

```solidity
function test_depositTo_wrapper_locks_funds() public {
    uint256 N = 1e18;
    altRsETH.mint(attacker, N);

    vm.startPrank(attacker);
    altRsETH.approve(address(wrapper), N);
    wrapper.depositTo(address(altRsETH), address(wrapper), N);
    vm.stopPrank();

    // wrsETH minted to wrapper itself — permanently locked
    assertEq(wrapper.balanceOf(address(wrapper)), N);

    // altRsETH held by wrapper — permanently locked (no one can burn wrapper's wrsETH)
    assertEq(altRsETH.balanceOf(address(wrapper)), N);

    // No recovery path: wrapper cannot call withdraw on itself
    // No recoverTokens/rescue function exists in RsETHTokenWrapper
}
```

### Citations

**File:** contracts/L2/RsETHTokenWrapper.sol (L77-79)
```text
    function depositTo(address asset, address _to, uint256 _amount) external {
        _deposit(asset, _to, _amount);
    }
```

**File:** contracts/L2/RsETHTokenWrapper.sol (L120-128)
```text
    function _withdraw(address _asset, address _to, uint256 _amount) internal {
        if (!allowedTokens[_asset]) revert TokenNotAllowed();

        _burn(msg.sender, _amount);

        ERC20Upgradeable(_asset).safeTransfer(_to, _amount);

        emit Withdraw(_asset, msg.sender, _to, _amount);
    }
```

**File:** contracts/L2/RsETHTokenWrapper.sol (L134-141)
```text
    function _deposit(address _asset, address _to, uint256 _amount) internal {
        if (!allowedTokens[_asset]) revert TokenNotAllowed();

        ERC20Upgradeable(_asset).safeTransferFrom(msg.sender, address(this), _amount);

        _mint(_to, _amount);
        emit Deposit(_asset, msg.sender, _to, _amount);
    }
```

**File:** contracts/utils/Recoverable.sol (L41-57)
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
        if (amount == 0) revert ZeroAmount();
        if (IERC20(tokenAddress).balanceOf(address(this)) < amount) revert InsufficientBalance();

        IERC20(tokenAddress).safeTransfer(recipient, amount);

        emit TokensRecovered(tokenAddress, recipient, amount);
    }
```

**File:** lib/openzeppelin-contracts-upgradeable/contracts/token/ERC20/extensions/ERC20WrapperUpgradeable.sol (L54-60)
```text
    function depositFor(address account, uint256 amount) public virtual returns (bool) {
        address sender = _msgSender();
        require(sender != address(this), "ERC20Wrapper: wrapper can't deposit");
        SafeERC20Upgradeable.safeTransferFrom(_underlying, sender, address(this), amount);
        _mint(account, amount);
        return true;
    }
```
