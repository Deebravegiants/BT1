### Title
`RSETHPool.deposit` and `RSETHPoolNoWrapper.deposit` fail when pool's pre-minted rsETH/wrsETH balance is exhausted - (File: contracts/pools/RSETHPool.sol, contracts/pools/RSETHPoolNoWrapper.sol)

### Summary
`RSETHPool.sol` and `RSETHPoolNoWrapper.sol` distribute rsETH/wrsETH to depositors by transferring from the pool's own pre-minted balance. There is no pre-check that the pool holds sufficient rsETH/wrsETH before accepting a deposit. When the pool's balance is exhausted, all deposit calls revert, making the pool temporarily unable to serve depositors.

### Finding Description
Both `RSETHPool.sol` and `RSETHPoolNoWrapper.sol` hold a finite, pre-minted supply of rsETH/wrsETH that is handed out to depositors via `safeTransfer`. This is structurally identical to the H-03 root cause: a function attempts to pay out tokens from the contract's own balance with no guarantee that balance is sufficient.

In `RSETHPool.sol`, both the ETH and token deposit paths call:

```solidity
IERC20(address(wrsETH)).safeTransfer(msg.sender, rsETHAmount);
``` [1](#0-0) [2](#0-1) 

In `RSETHPoolNoWrapper.sol`, both deposit paths call:

```solidity
rsETH.safeTransfer(msg.sender, rsETHAmount);
``` [3](#0-2) [4](#0-3) 

Neither function checks whether `IERC20(wrsETH).balanceOf(address(this))` or `rsETH.balanceOf(address(this))` is sufficient before accepting the deposit. The pool's balance is finite and decreases with every successful deposit. Once exhausted, every subsequent `safeTransfer` reverts, and the pool stops functioning as a deposit venue.

This contrasts directly with the newer pool variants — `RSETHPoolV3`, `RSETHPoolV2ExternalBridge`, `RSETHPoolV3ExternalBridge`, and `RSETHPoolV3WithNativeChainBridge` — which all call `wrsETH.mint(msg.sender, rsETHAmount)` and are therefore not constrained by a finite pool balance: [5](#0-4) [6](#0-5) 

The protocol's own upgrade history confirms this: the `mint`-based approach is the intended fix, but `RSETHPool.sol` and `RSETHPoolNoWrapper.sol` were never migrated.

### Impact Explanation
**Low — Contract fails to deliver promised returns, but doesn't lose value.**

When the pool's rsETH/wrsETH balance is zero, every call to `deposit()` reverts atomically. For the ETH deposit path, `msg.value` is returned to the caller. For the token deposit path, `safeTransferFrom` is also reverted, so the user's tokens are returned. No funds are permanently lost. However, the pool is completely unable to accept new deposits until the BRIDGER role replenishes it, meaning the contract fails to deliver its core promised service.

### Likelihood Explanation
This is a normal operational condition, not an edge case. The pool's rsETH/wrsETH balance decreases monotonically with every deposit. Under sustained deposit demand — which is the expected operating condition for an active L2 liquidity pool — the balance will be exhausted. The replenishment path (BRIDGER calling `L1Vault.bridgeRsETHToL2`) introduces latency, during which the pool is non-functional. [7](#0-6) [8](#0-7) 

### Recommendation
Add an explicit balance check before accepting the deposit, and revert with a descriptive error if the pool cannot fulfill the request:

```solidity
if (IERC20(address(wrsETH)).balanceOf(address(this)) < rsETHAmount)
    revert InsufficientWrsETHBalance();
```

The preferred long-term fix — already applied in all newer pool variants — is to replace `safeTransfer` with `wrsETH.mint(msg.sender, rsETHAmount)`, eliminating the dependency on a finite pre-minted balance entirely.

### Proof of Concept
1. `RSETHPool` on Arbitrum is seeded with 1,000 wrsETH.
2. Users deposit ETH over time; the pool distributes wrsETH until its balance reaches 0.
3. A new user calls `deposit{value: 1 ether}("ref")`.
4. `viewSwapRsETHAmountAndFee(1 ether)` returns `rsETHAmount = 0.95e18`.
5. `IERC20(address(wrsETH)).safeTransfer(msg.sender, 0.95e18)` reverts because `balanceOf(pool) == 0`.
6. The entire transaction reverts; the user's 1 ETH is returned.
7. All subsequent deposit attempts fail identically until the BRIDGER replenishes the pool via `L1Vault.bridgeRsETHToL2`. [7](#0-6) [8](#0-7)

### Citations

**File:** contracts/pools/RSETHPool.sol (L265-278)
```text
    function deposit(string memory referralId) external payable nonReentrant whenNotPaused {
        if (!isEthDepositEnabled) revert EthDepositDisabled();
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        IERC20(address(wrsETH)).safeTransfer(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }
```

**File:** contracts/pools/RSETHPool.sol (L302-302)
```text
        IERC20(address(wrsETH)).safeTransfer(msg.sender, rsETHAmount);
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L231-244)
```text
    function deposit(string memory referralId) external payable nonReentrant whenNotPaused {
        if (!isEthDepositEnabled) revert EthDepositDisabled();
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        rsETH.safeTransfer(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L268-268)
```text
        rsETH.safeTransfer(msg.sender, rsETHAmount);
```

**File:** contracts/pools/RSETHPoolV3.sol (L262-262)
```text
        wrsETH.mint(msg.sender, rsETHAmount);
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L381-381)
```text
        wrsETH.mint(msg.sender, rsETHAmount);
```
