### Title
Blocked Users Can Bypass `RSETH` Transfer Restrictions via L2 Pool Deposits to Receive `wrsETH` - (File: contracts/pools/RSETHPoolV3.sol, contracts/pools/RSETHPoolV3ExternalBridge.sol)

---

### Summary

`RSETH.sol` implements a `blockUserTransfers` mechanism that prevents a blocked address from receiving or transferring `rsETH`. However, the L2 deposit pools (`RSETHPoolV3` and `RSETHPoolV3ExternalBridge`) mint `wrsETH` directly to depositors without checking whether the recipient is blocked on L1. A user blocked on L1 can deposit ETH or LSTs on any supported L2 and receive `wrsETH` — an economically equivalent rsETH position — bypassing the intended regulatory freeze entirely.

---

### Finding Description

`RSETH.sol` enforces a transfer block via `transfersBlockedUntil` and `_enforceNotBlocked()`: [1](#0-0) 

The `mint()` function enforces this check before minting rsETH to any recipient: [2](#0-1) 

The `_transfer()` override also enforces it on both sender and receiver: [3](#0-2) 

The admin can also recover rsETH from a blocked user via `recoverFrozenFunds()`: [4](#0-3) 

However, the L2 pools bypass all of this. `RSETHPoolV3.deposit()` calls `wrsETH.mint(msg.sender, rsETHAmount)` directly: [5](#0-4) [6](#0-5) 

`RSETHPoolV3ExternalBridge.deposit()` does the same: [7](#0-6) [8](#0-7) 

The `wrsETH` token is `RsETHTokenWrapper`, whose `mint()` function has no connection to the L1 `RSETH.sol` block list: [9](#0-8) 

`RsETHTokenWrapper` is a plain ERC20 with no `_enforceNotBlocked` override, so `wrsETH` transfers are completely unrestricted regardless of the L1 block state. [10](#0-9) 

---

### Impact Explanation

A user blocked on L1 via `blockUserTransfers` can:

1. Deposit ETH or LSTs on any supported L2 (Arbitrum, Base, Optimism, etc.) through `RSETHPoolV3.deposit()` or `RSETHPoolV3ExternalBridge.deposit()`.
2. Receive `wrsETH` directly — an rsETH-equivalent yield-bearing position — with no block check applied.
3. Freely transfer `wrsETH` to any address (no restriction on `RsETHTokenWrapper` transfers).
4. Route `wrsETH` to an unblocked address, which can then call `RsETHTokenWrapper.withdraw()` to redeem the underlying rsETH on L1, fully circumventing the freeze.

Additionally, `recoverFrozenFunds()` in `RSETH.sol` only operates on L1 `rsETH` balances. It cannot recover `wrsETH` held by a blocked user on L2, leaving the admin with no enforcement path against the bypassed position.

**Impact**: Medium — temporary freezing of funds is bypassed; the admin's ability to freeze and recover a user's rsETH-equivalent position is broken.

---

### Likelihood Explanation

Any user who has been blocked via `blockUserTransfers` and holds ETH or supported LSTs can immediately exploit this by calling the public `deposit()` function on any deployed L2 pool. No special privileges, front-running, or external dependencies are required. The L2 pools are publicly accessible entry points.

---

### Recommendation

In `RSETHPoolV3.deposit()` and `RSETHPoolV3ExternalBridge.deposit()`, before calling `wrsETH.mint(msg.sender, ...)`, query the L1 block status of `msg.sender`. Since this is a cross-chain check, the recommended approach is to maintain a mirrored blocklist on each L2 (synchronized from L1 via the existing cross-chain rate/message infrastructure) and enforce it in the L2 pool's deposit path. Alternatively, expose a `isBlocked(address)` view on `wrsETH` that the L2 pool checks before minting.

---

### Proof of Concept

**Scenario:**

1. On Ethereum L1, the admin calls `RSETH.blockUserTransfers([victim])`, setting `transfersBlockedUntil[victim] = block.timestamp + 1 days`. Any attempt to mint or transfer rsETH to/from `victim` on L1 now reverts with `TransfersBlocked`.

2. `victim` holds ETH on Arbitrum (or any supported L2). They call `RSETHPoolV3.deposit{value: 10 ether}("ref")` on the Arbitrum pool.

3. Inside `deposit()`, `wrsETH.mint(msg.sender, rsETHAmount)` is called. `RsETHTokenWrapper.mint()` has no block check and succeeds, crediting `victim` with `wrsETH`.

4. `victim` now holds a full rsETH-equivalent position in `wrsETH` on L2, freely transferable. They transfer it to an unblocked address `other`, which calls `RsETHTokenWrapper.withdraw(rsETH, amount)` to redeem the underlying rsETH on L1 — the freeze is fully bypassed.

5. `recoverFrozenFunds(victim)` on L1 finds zero rsETH balance for `victim` and recovers nothing. [11](#0-10) [12](#0-11) [13](#0-12)

### Citations

**File:** contracts/RSETH.sol (L161-177)
```text
    function blockUserTransfers(address[] calldata accounts) external onlyLRTManager {
        uint256 blockedUntil = block.timestamp + 1 days;
        uint256 length = accounts.length;

        for (uint256 i = 0; i < length; ++i) {
            address account = accounts[i];

            if (isPermanentlyExempt[account] || account == address(0)) continue;

            uint256 prevBlockedUntil = transfersBlockedUntil[account];

            if (blockedUntil != prevBlockedUntil) {
                transfersBlockedUntil[account] = blockedUntil;
                emit UserTransfersBlocked(account, blockedUntil);
            }
        }
    }
```

**File:** contracts/RSETH.sol (L206-219)
```text
    function recoverFrozenFunds(address from) external onlyLRTAdmin {
        UtilLib.checkNonZeroAddress(from);
        UtilLib.checkNonZeroAddress(custodyAddress);

        if (isPermanentlyExempt[from]) revert AddressPermanentlyExempt(from);

        uint256 blockedUntil = transfersBlockedUntil[from];
        if (blockedUntil == 0 || block.timestamp >= blockedUntil) revert NoActiveTransferBlock(from);

        uint256 accountBalance = balanceOf(from);

        // Bypass transfer block enforcement when transferring to custody address
        super._transfer(from, custodyAddress, accountBalance);
        emit FrozenFundsRecovered(from, custodyAddress, accountBalance);
```

**File:** contracts/RSETH.sol (L229-240)
```text
    function mint(
        address to,
        uint256 amount
    )
        external
        onlyRole(LRTConstants.MINTER_ROLE)
        whenNotPaused
        checkDailyMintLimit(amount)
    {
        _enforceNotBlocked(to);
        _mint(to, amount);
    }
```

**File:** contracts/RSETH.sol (L287-291)
```text
    function _transfer(address from, address to, uint256 amount) internal override {
        _enforceNotBlocked(from);
        _enforceNotBlocked(to);
        super._transfer(from, to, amount);
    }
```

**File:** contracts/RSETH.sol (L294-306)
```text
    function _enforceNotBlocked(address account) internal {
        // Addresses that are permanently exempt can never be blocked
        if (isPermanentlyExempt[account]) return;

        // Check if the account has an active transfer block
        uint256 blockedUntil = transfersBlockedUntil[account];
        if (blockedUntil == 0) return;

        if (block.timestamp < blockedUntil) revert TransfersBlocked(account, blockedUntil);

        // Auto-clean up expired block
        delete transfersBlockedUntil[account];
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L246-265)
```text
    function deposit(string memory referralId)
        external
        payable
        nonReentrant
        whenNotPaused
        limitDailyMint(msg.value, ETH_IDENTIFIER)
    {
        if (!isEthDepositEnabled) revert EthDepositDisabled();
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L271-293)
```text
    function deposit(
        address token,
        uint256 amount,
        string memory referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedToken(token)
        limitDailyMint(amount, token)
    {
        if (amount == 0) revert InvalidAmount();

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId, token);
    }
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L366-384)
```text
    function deposit(string memory referralId)
        external
        payable
        nonReentrant
        whenNotPaused
        limitDailyMint(msg.value, ETH_IDENTIFIER)
    {
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L390-412)
```text
    function deposit(
        address token,
        uint256 amount,
        string memory referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedToken(token)
        limitDailyMint(amount, token)
    {
        if (amount == 0) revert InvalidAmount();

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId, token);
    }
```

**File:** contracts/L2/RsETHTokenWrapper.sol (L20-29)
```text
contract RsETHTokenWrapper is Initializable, AccessControlUpgradeable, ERC20Upgradeable, ERC20PermitUpgradeable {
    using SafeERC20Upgradeable for ERC20Upgradeable;

    /// @dev The address of the alternative RsETH token
    mapping(address allowedToken => bool isAllowed) public allowedTokens;

    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant BRIDGER_ROLE = keccak256("BRIDGER_ROLE");
    bytes32 public constant TIMELOCK_ROLE = keccak256("TIMELOCK_ROLE");

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

**File:** contracts/L2/RsETHTokenWrapper.sol (L190-193)
```text
    function mint(address _to, uint256 _amount) external onlyRole(MINTER_ROLE) {
        _mint(_to, _amount);
    }
}
```
