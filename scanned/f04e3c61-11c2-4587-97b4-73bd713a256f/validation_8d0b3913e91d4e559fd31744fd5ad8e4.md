### Title
`RSETHPoolNoWrapper.deposit()` Bypasses `startTimestamp` Initialization Guard Present in Every Other Pool Variant — (File: `contracts/pools/RSETHPoolNoWrapper.sol`)

---

### Summary

`RSETHPoolNoWrapper` is the only production pool contract in the repository that has **no `startTimestamp` variable and no `limitDailyMint` guard**. Every other pool variant enforces `if (block.timestamp < startTimestamp) revert MintBeforeStartTimestamp()` before any rsETH is issued. Because `RSETHPoolNoWrapper` omits this guard entirely, any unprivileged caller can invoke `deposit()` and receive rsETH immediately after contract deployment — before the operator has set an intended launch time — with no time-based initialization barrier.

---

### Finding Description

Every other L2 pool contract in the repository declares a `startTimestamp` storage variable and enforces it inside a `limitDailyMint` modifier that is applied to every `deposit()` entry point:

**`RSETHPoolV3.sol` (representative of V2, V2ExternalBridge, V3, V3ExternalBridge, V3WithNativeChainBridge):**
```solidity
modifier limitDailyMint(uint256 amount, address token) {
    if (block.timestamp < startTimestamp) {
        revert MintBeforeStartTimestamp();   // ← initialization gate
    }
    ...
}
``` [1](#0-0) 

The `startTimestamp` is set via a separate `reinitialize()` call that enforces it must be in the future:
```solidity
if (block.timestamp > _startTimestamp) {
    revert InvalidStartTimestamp();
}
``` [2](#0-1) 

`RSETHPoolNoWrapper`, by contrast, declares **no `startTimestamp` variable** and its `deposit()` functions carry only `whenNotPaused`:

```solidity
function deposit(string memory referralId) external payable nonReentrant whenNotPaused {
    if (!isEthDepositEnabled) revert EthDepositDisabled();
    ...
    rsETH.safeTransfer(msg.sender, rsETHAmount);
    ...
}
``` [3](#0-2) 

```solidity
function deposit(
    address token,
    uint256 amount,
    string memory referralId
)
    external
    nonReentrant
    whenNotPaused
    onlySupportedToken(token)
{
``` [4](#0-3) 

There is no `limitDailyMint` modifier, no `startTimestamp` field, and no `reinitialize()` overload that sets one. The contract's `initialize()` sets `paused` to its default (`false`) and `isEthDepositEnabled` to whatever the deployer passes — meaning deposits are live the moment the proxy is initialized unless the deployer separately calls `pause()`. [5](#0-4) 

---

### Impact Explanation

**Low — Contract fails to deliver promised returns, but doesn't lose value.**

`RSETHPoolNoWrapper` transfers pre-loaded rsETH from its own balance to depositors. The exchange rate is oracle-determined (`rsETHOracle.getRate()`), so there is no pool-price advantage to depositing early. However:

1. The operator cannot schedule a future launch time for this pool the way every other pool variant can. The only lever is `pause()`, which must be called proactively.
2. If the contract is deployed with rsETH already pre-loaded (required for the pool to function) and the deployer does not immediately pause it, any watcher can drain the pre-loaded rsETH inventory at the current oracle rate before the intended public launch, consuming the daily-equivalent capacity that the operator expected to control.
3. The inconsistency with all sibling contracts means operators applying the same deployment runbook (set `startTimestamp` via `reinitialize`) will find no such function exists on this contract, creating an operational gap.

---

### Likelihood Explanation

**Medium.** `RSETHPoolNoWrapper` is the active pool for Arbitrum and Unichain (per the wiki). Deployment of an upgradeable proxy and pre-loading of rsETH are distinct transactions. Any block between those two steps — or any deployment where the operator forgets to call `pause()` — opens the window. MEV bots and on-chain watchers routinely monitor new contract deployments for exactly this pattern.

---

### Recommendation

Add a `startTimestamp` storage variable and a `limitDailyMint` modifier to `RSETHPoolNoWrapper`, mirroring the pattern in `RSETHPoolV3`:

```solidity
uint256 public startTimestamp;

modifier limitDailyMint(uint256 amount, address token) {
    if (block.timestamp < startTimestamp) revert MintBeforeStartTimestamp();
    // ... daily cap logic ...
    _;
}
```

Apply `limitDailyMint` to both `deposit()` overloads, and add a `reinitialize()` function (guarded by `DEFAULT_ADMIN_ROLE`) that sets `startTimestamp` to a future value, consistent with `RSETHPoolV3.reinitialize()`. [6](#0-5) 

---

### Proof of Concept

1. Operator deploys `RSETHPoolNoWrapper` proxy and calls `initialize(admin, manager, rsETH, feeBps, oracle, true)`. Contract is live, not paused.
2. Operator sends a separate transaction to pre-load rsETH into the contract (required for `deposit()` to work).
3. Attacker observes step 2 in the mempool and front-runs or immediately follows with `deposit{value: X}("")`.
4. `whenNotPaused` passes (contract not paused), `isEthDepositEnabled` passes (set to `true` in step 1), no `startTimestamp` check exists — `rsETH.safeTransfer(msg.sender, rsETHAmount)` executes.
5. Attacker receives rsETH from the pool's pre-loaded inventory before the operator's intended public launch, consuming capacity the operator expected to control via a scheduled `startTimestamp`. [3](#0-2) [7](#0-6)

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L96-99)
```text
    modifier limitDailyMint(uint256 amount, address token) {
        if (block.timestamp < startTimestamp) {
            revert MintBeforeStartTimestamp();
        }
```

**File:** contracts/pools/RSETHPoolV3.sol (L179-198)
```text
    function reinitialize(
        uint256 _dailyMintLimit,
        uint256 _startTimestamp
    )
        external
        reinitializer(2)
        onlyRole(DEFAULT_ADMIN_ROLE)
    {
        if (_dailyMintLimit == 0) {
            revert InvalidDailyMintLimit();
        }

        // startTimestamp cannot be in the past
        if (block.timestamp > _startTimestamp) {
            revert InvalidStartTimestamp();
        }

        dailyMintLimit = _dailyMintLimit;
        startTimestamp = _startTimestamp;
    }
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L190-217)
```text
    function initialize(
        address admin,
        address manager,
        address _rsETH,
        uint256 _feeBps,
        address _rsETHOracle,
        bool _isEthDepositEnabled
    )
        external
        initializer
    {
        UtilLib.checkNonZeroAddress(admin);
        UtilLib.checkNonZeroAddress(manager);
        UtilLib.checkNonZeroAddress(_rsETH);
        UtilLib.checkNonZeroAddress(_rsETHOracle);

        __AccessControl_init();
        __Pausable_init();
        __ReentrancyGuard_init();

        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(BRIDGER_ROLE, manager);

        rsETH = IERC20(_rsETH);
        feeBps = _feeBps;
        rsETHOracle = _rsETHOracle;
        isEthDepositEnabled = _isEthDepositEnabled;
    }
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

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L250-271)
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
    {
        if (amount == 0) revert InvalidAmount();

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        rsETH.safeTransfer(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId); // Add token address?
    }
```
