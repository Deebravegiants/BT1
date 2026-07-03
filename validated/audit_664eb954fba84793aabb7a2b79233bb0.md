### Title
Users Lose Gas Fees When Depositing Into a Paused L2 Pool - (File: contracts/pools/RSETHPoolNoWrapper.sol)

### Summary
All L2 pool contracts in the LRT-rsETH protocol implement a pause mechanism. When a pool is paused, any user `deposit()` call reverts, causing the user to lose gas fees without receiving rsETH. No on-chain or protocol-enforced mechanism warns users before they submit a transaction to a paused pool.

### Finding Description
Five pool contracts implement a `whenNotPaused` guard on their public `deposit()` entry points:

- `RSETHPoolNoWrapper` uses OpenZeppelin `PausableUpgradeable` and applies `whenNotPaused` to both `deposit(string)` (ETH) and `deposit(address,uint256,string)` (token).
- `RSETHPool`, `RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, and `RSETHPoolV2ExternalBridge` each declare a custom `bool public paused` storage variable and a hand-rolled `whenNotPaused` modifier that reverts with `ContractPaused()`.

In every case the pause check is the first substantive modifier to execute. For ETH deposits the user has already committed `msg.value` to the call; for token deposits the `safeTransferFrom` is inside the function body and therefore never executes. On revert the EVM returns the ETH, but the gas consumed by the failed call is permanently lost.

The `PAUSER_ROLE` can pause any pool at any time without a timelock. A user who submits a deposit transaction while the pool is unpaused may have it mined after a pause event, or may simply be unaware that the pool is already paused, and will lose gas fees with no recourse.

Relevant code paths:

`RSETHPoolNoWrapper.deposit(string)` — `whenNotPaused` at line 231: [1](#0-0) 

`RSETHPoolNoWrapper.deposit(address,uint256,string)` — `whenNotPaused` at line 257: [2](#0-1) 

`RSETHPoolNoWrapper.pause()` callable by `PAUSER_ROLE` with no timelock: [3](#0-2) 

Same pattern in `RSETHPool`: [4](#0-3) [5](#0-4) 

Same pattern in `RSETHPoolV3`: [6](#0-5) [7](#0-6) 

Same pattern in `RSETHPoolV3ExternalBridge`: [8](#0-7) [9](#0-8) 

### Impact Explanation
When a pool is paused, every user deposit transaction reverts. The user's ETH or ERC-20 tokens are returned by the EVM, but the gas fee paid for the failed transaction is permanently lost. The contract fails to deliver the promised rsETH/wrsETH while the user bears a direct, if small, financial cost. This maps to **Low — contract fails to deliver promised returns, but doesn't lose deposited value**.

### Likelihood Explanation
The `PAUSER_ROLE` can pause any pool instantly and without a timelock. Pauses are expected to occur during emergencies, upgrades, or oracle anomalies. Because L2 block times are short and mempool visibility is limited, a user can easily submit a deposit transaction moments before or during a pause event and have it revert. No on-chain signal prevents this.

### Recommendation
Mirror the external report's recommendation: expose the `paused` state prominently in the front-end so users are warned before submitting a deposit transaction to a paused pool. Additionally, consider emitting a standardised event (already present: `Paused`/`Unpaused`) that front-end monitoring can consume to update UI state in real time.

### Proof of Concept
1. `PAUSER_ROLE` calls `RSETHPoolNoWrapper.pause()` — `paused` state is set.
2. User calls `RSETHPoolNoWrapper.deposit{value: 1 ether}("ref")`.
3. `whenNotPaused` modifier fires immediately, reverting with `EnforcedPause` (OZ) before any state change.
4. The 1 ETH is returned to the user; the gas cost of the failed transaction (~21 000 + call overhead) is permanently deducted from the user's wallet.
5. The same outcome applies to token deposits across all five pool contracts listed above.

### Citations

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

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L672-675)
```text
    /// @dev Pauses the pausable methods in the contract
    function pause() external onlyRole(PAUSER_ROLE) whenNotPaused {
        _pause();
    }
```

**File:** contracts/pools/RSETHPool.sol (L90-93)
```text
    modifier whenNotPaused() {
        if (paused) revert ContractPaused();
        _;
    }
```

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

**File:** contracts/pools/RSETHPoolV3.sol (L71-74)
```text
    modifier whenNotPaused() {
        if (paused) revert ContractPaused();
        _;
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

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L105-108)
```text
    modifier whenNotPaused() {
        if (paused) revert ContractPaused();
        _;
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
