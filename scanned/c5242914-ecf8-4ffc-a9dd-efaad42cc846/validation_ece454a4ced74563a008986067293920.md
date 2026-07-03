### Title
`wrsETH` wrapper address is permanently locked after initialization, forcing full pool redeployment if it ever needs to change - (File: `contracts/pools/RSETHPoolV3.sol`)

---

### Summary

`RSETHPoolV3` and `RSETHPoolV3ExternalBridge` set the `wrsETH` (RsETHTokenWrapper) address once in `initialize()` with no admin setter to update it. If the wrapper contract must be replaced, the pool contract must be redeployed from scratch, losing all accumulated fee state and temporarily breaking L2 deposits for rsETH holders.

---

### Finding Description

In `RSETHPoolV3.sol`, the `wrsETH` state variable is assigned during `initialize()` and is never updatable afterward:

```solidity
// contracts/pools/RSETHPoolV3.sol  line 228
wrsETH = IERC20WrsETH(_wrsETH);
```

The contract exposes setters for every other critical address — `rsETHOracle` via `setRSETHOracle`, `supportedTokenOracle` via `setSupportedTokenOracle`, `dailyMintLimit` via `setDailyMintLimit` — but no equivalent `setWrsETH` function exists anywhere in the contract.

`wrsETH` is used in two critical paths:

1. **`deposit()`** — calls `wrsETH.mint(msg.sender, rsETHAmount)` to issue wrapped rsETH to every depositor.
2. **`swapAssetToPremintedRsETH()`** — casts `wrsETH` to `IRsETHTokenWrapper` and calls `wrapper.allowedTokens(rsETH)` and `wrapper.maxAmountToDepositBridgerAsset(rsETH)`.

The identical pattern exists in `RSETHPoolV3ExternalBridge.sol` at line 349:

```solidity
// contracts/pools/RSETHPoolV3ExternalBridge.sol  line 349
wrsETH = IERC20WrsETH(_wrsETH);
```

Neither contract provides any mechanism to update `wrsETH` post-deployment.

---

### Impact Explanation

**Low — Contract fails to deliver promised returns, but doesn't lose value.**

If the `RsETHTokenWrapper` contract must be replaced (e.g., a critical bug is found in the wrapper that cannot be patched via its own upgrade, or the wrapper's proxy admin key is compromised and a fresh deployment is required), the pool contract itself must be redeployed. Consequences:

- All accumulated `feeEarnedInETH` and `feeEarnedInToken` balances are stranded in the old pool unless manually swept first.
- The `dailyMintAmount` / `lastMintDay` / `startTimestamp` state is lost, requiring re-initialization.
- Every off-chain integration, bridger, and dependent contract pointing to the pool address must be updated.
- During the migration window, L2 users cannot deposit ETH or supported tokens to receive rsETH, breaking the core L2 deposit path.

No user funds are directly stolen, but the protocol's ability to deliver rsETH to depositors is temporarily frozen.

---

### Likelihood Explanation

Low. The `RsETHTokenWrapper` is itself an upgradeable proxy, so most fixes can be applied without changing its address. However, scenarios that would require a fresh deployment — proxy admin key compromise, storage-layout-breaking upgrade, or a critical initialization bug — are realistic over a multi-year protocol lifetime. The absence of a setter makes the pool permanently fragile to any such event.

---

### Recommendation

Add a privileged setter (guarded by `TIMELOCK_ROLE`) to both `RSETHPoolV3` and `RSETHPoolV3ExternalBridge`:

```solidity
function setWrsETH(address _wrsETH) external onlyRole(TIMELOCK_ROLE) {
    UtilLib.checkNonZeroAddress(_wrsETH);
    wrsETH = IERC20WrsETH(_wrsETH);
    emit WrsETHSet(_wrsETH);
}
```

This mirrors the pattern already used for `rsETHOracle` (`setRSETHOracle`) and `stargatePool` (`setStargatePool`) in the same contracts.

---

### Proof of Concept

1. `RSETHPoolV3` is deployed with `wrsETH = WrapperV1`.
2. A critical vulnerability is discovered in `WrapperV1` that cannot be patched via its proxy upgrade (e.g., storage collision introduced by a prior upgrade).
3. Protocol deploys `WrapperV2` at a new address.
4. There is no function in `RSETHPoolV3` to call `setWrsETH(WrapperV2)`.
5. Every call to `deposit()` continues to invoke `WrapperV1.mint(...)`, which is now broken or compromised.
6. L2 depositors receive zero rsETH or the transaction reverts, freezing the L2 deposit path until the pool is fully redeployed. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L207-232)
```text
    function initialize(
        address admin,
        address bridger,
        address _wrsETH,
        uint256 _feeBps,
        address _rsETHOracle,
        bool _isEthDepositEnabled
    )
        external
        initializer
    {
        UtilLib.checkNonZeroAddress(_wrsETH);
        UtilLib.checkNonZeroAddress(_rsETHOracle);

        __ERC20_init("rsETH", "rsETH");
        __AccessControl_init();
        __ReentrancyGuard_init();

        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _setupRole(BRIDGER_ROLE, bridger);

        wrsETH = IERC20WrsETH(_wrsETH);
        feeBps = _feeBps;
        rsETHOracle = _rsETHOracle;
        isEthDepositEnabled = _isEthDepositEnabled;
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L258-265)
```text
        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L330-352)
```text
    function initialize(
        address admin,
        address bridger,
        address _wrsETH,
        uint256 _feeBps,
        address _rsETHOracle
    )
        external
        initializer
    {
        UtilLib.checkNonZeroAddress(_wrsETH);
        UtilLib.checkNonZeroAddress(_rsETHOracle);
        __ERC20_init("rsETH", "rsETH");
        __AccessControl_init();
        __ReentrancyGuard_init();
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _setupRole(BRIDGER_ROLE, admin);
        _setupRole(BRIDGER_ROLE, bridger);

        wrsETH = IERC20WrsETH(_wrsETH);
        feeBps = _feeBps;
        rsETHOracle = _rsETHOracle;
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
