### Title
`RsETHTokenWrapper.mint()` Is Permanently Inaccessible to L2 Pool Contracts Due to Missing `MINTER_ROLE` Grant in `initialize()` - (File: contracts/L2/RsETHTokenWrapper.sol)

### Summary
`RsETHTokenWrapper.initialize()` never grants `MINTER_ROLE` to any address. All three L2 pool variants (`RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`) call `wrsETH.mint()` inside their public `deposit()` functions, but none of them hold `MINTER_ROLE` on the wrapper. Every user deposit reverts at the mint step until an admin manually grants the role out-of-band.

### Finding Description
`RsETHTokenWrapper.mint()` is gated by `onlyRole(MINTER_ROLE)`:

```solidity
// contracts/L2/RsETHTokenWrapper.sol:190
function mint(address _to, uint256 _amount) external onlyRole(MINTER_ROLE) {
    _mint(_to, _amount);
}
```

`RsETHTokenWrapper.initialize()` sets up only `DEFAULT_ADMIN_ROLE` and `BRIDGER_ROLE`; `MINTER_ROLE` is never granted to anyone:

```solidity
// contracts/L2/RsETHTokenWrapper.sol:55-64
function initialize(address admin, address bridger, address _altRsETH) external initializer {
    __ERC20_init("rsETHWrapper", "wrsETH");
    __ERC20Permit_init("rsETHWrapper");
    __AccessControl_init();

    _setupRole(DEFAULT_ADMIN_ROLE, admin);
    _setupRole(BRIDGER_ROLE, bridger);   // MINTER_ROLE is absent

    _addAllowedToken(_altRsETH);
}
```

`reinitialize()` also does not grant `MINTER_ROLE`:

```solidity
// contracts/L2/RsETHTokenWrapper.sol:47-49
function reinitialize(address _altRsETH) external reinitializer(2) onlyRole(DEFAULT_ADMIN_ROLE) {
    _addAllowedToken(_altRsETH);
}
```

All three pool variants call `wrsETH.mint()` as the final step of every deposit:

- `RSETHPoolV3.deposit()` — lines 262 and 290
- `RSETHPoolV3ExternalBridge.deposit()` — lines 381 and 409
- `RSETHPoolV3WithNativeChainBridge.deposit()` — lines 298 and 326

None of these pool contracts are granted `MINTER_ROLE` on `RsETHTokenWrapper` during their own `initialize()` calls either. The call chain is:

```
user → RSETHPoolV3.deposit()
         → wrsETH.mint(msg.sender, rsETHAmount)   // AccessControl revert: missing MINTER_ROLE
```

### Impact Explanation
Every user-facing `deposit()` call across all L2 pool variants reverts at the `wrsETH.mint()` step. For ERC-20 deposits the token `safeTransferFrom` executes before the mint call, but the revert unwinds the entire transaction so no tokens are lost. For ETH deposits `msg.value` is similarly returned on revert. No funds are permanently lost, but the entire L2 deposit surface is non-functional from the moment of deployment until an admin separately calls `grantRole(MINTER_ROLE, poolAddress)` on `RsETHTokenWrapper`.

**Impact: Low — Contract fails to deliver promised returns, but doesn't lose value.**

### Likelihood Explanation
This triggers on the very first deposit attempt after deployment. Any unprivileged user calling `deposit()` on any L2 pool will hit the revert. The missing role grant is structural — it is absent from every initialization path — so the failure is deterministic and immediate.

### Recommendation
Grant `MINTER_ROLE` to the pool contract inside `RsETHTokenWrapper.initialize()`, or alternatively inside each pool's own `initialize()` by calling `wrsETH.grantRole(MINTER_ROLE, address(this))` (which requires the pool to hold `DEFAULT_ADMIN_ROLE` on the wrapper at that point). The cleanest fix is to add the grant directly in the wrapper's initializer:

```diff
function initialize(address admin, address bridger, address _altRsETH) external initializer {
    __ERC20_init("rsETHWrapper", "wrsETH");
    __ERC20Permit_init("rsETHWrapper");
    __AccessControl_init();

    _setupRole(DEFAULT_ADMIN_ROLE, admin);
    _setupRole(BRIDGER_ROLE, bridger);
+   // Grant MINTER_ROLE to the pool contract that will call mint()
+   // (pass pool address as a constructor/initializer parameter)
+   _setupRole(MINTER_ROLE, pool);

    _addAllowedToken(_altRsETH);
}
```

### Proof of Concept
1. Deploy `RsETHTokenWrapper` and call `initialize(admin, bridger, altRsETH)`.
2. Deploy `RSETHPoolV3` and call `initialize(admin, bridger, wrsETH, feeBps, oracle, true)`.
3. Call `RSETHPoolV3.deposit{value: 1 ether}("")` as any user.
4. The call reverts at `wrsETH.mint(msg.sender, rsETHAmount)` with an `AccessControl` missing-role error because `RSETHPoolV3` was never granted `MINTER_ROLE` on `RsETHTokenWrapper`. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

**File:** contracts/L2/RsETHTokenWrapper.sol (L55-64)
```text
    function initialize(address admin, address bridger, address _altRsETH) external initializer {
        __ERC20_init("rsETHWrapper", "wrsETH");
        __ERC20Permit_init("rsETHWrapper");
        __AccessControl_init();

        _setupRole(DEFAULT_ADMIN_ROLE, admin);
        _setupRole(BRIDGER_ROLE, bridger);

        _addAllowedToken(_altRsETH);
    }
```

**File:** contracts/L2/RsETHTokenWrapper.sol (L187-192)
```text
    /// @dev Mint wrsETH tokens on L2
    /// @param _to The address to mint the tokens to
    /// @param _amount The amount of tokens to mint
    function mint(address _to, uint256 _amount) external onlyRole(MINTER_ROLE) {
        _mint(_to, _amount);
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L258-264)
```text
        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
```

**File:** contracts/pools/RSETHPoolV3.sol (L286-292)
```text
        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId, token);
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L378-383)
```text

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
```

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L295-300)
```text

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
```
