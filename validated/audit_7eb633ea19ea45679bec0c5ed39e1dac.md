## Analog Found

### Title
Missing zero-address validation in `EvmHost` constructor permanently bricks `initialize` and the host's message-delivery route - ([File: evm/src/core/EvmHost.sol])

### Summary
`EvmHost`'s constructor accepts an `admin` address with no validation, unlike the sibling `HostManager` contract which explicitly rejects `address(0)` in its constructor.

### Finding Description
The `EvmHost` constructor stores the supplied `_admin` directly into `_hostParams.admin` with no zero-address check: [1](#0-0) 

The one-shot `initialize` function is gated exclusively on this admin value: [2](#0-1) 

By contrast, the sibling `HostManager` contract explicitly guards against this exact class of bug, reverting with `InvalidAdmin` if its admin parameter is zero: [3](#0-2) 

`EvmHost` has no equivalent check. Furthermore, `updateHostParamsInternal`, which validates `hostManager`, `handler`, and `consensusClient` against `address(0)` and interface support before writing new `HostParams`, never validates `params.admin` before overwriting `_hostParams.admin`: [4](#0-3) 

If `EvmHost` is deployed with `admin == address(0)` (misconfigured deploy script, wrong environment variable, CREATE2 salt/calldata mixup, etc.), no account can ever satisfy `_msgSender() == _hostParams.admin` in `initialize`, since a transaction's `msg.sender` can never be `address(0)`. The host therefore can never be initialized: `hostManager`, `handler`, `consensusClient`, `feeToken`, and `hyperbridge` id remain unset forever, and `_initialized` never flips to `true`.

### Impact Explanation
An uninitialized `EvmHost` cannot dispatch or receive any ISMP message: `handler`/`consensusClient`/`hostManager` are all zero, so `HandlerV2` calls against this host and any request/response processing will revert or operate on meaningless state. This is a permanent "route unable to deliver messages" condition for that deployment — the entire chain endpoint of Hyperbridge becomes irrecoverably dead with no governance path to fix it, since fixing it requires a `SetHostParam`/`UpdateParams` cross-chain governance message delivered *through the very host that cannot be initialized*.

### Likelihood Explanation
This requires only a deployment-time mistake, not smart-contract-level malicious activity — a wrong constructor argument (e.g., a template config defaulting to `address(0)`, a chain-specific env var missing) is the only precondition. Given `EvmHost` is deployed per supported chain (as seen in `DeployIsmp.s.sol` and Tron migration scripts using an `admin` variable pulled from config/env), the risk of a zero/blank admin slipping through on any given chain deployment is non-trivial, and the resulting failure mode (permanent host bricking) is unrecoverable. [5](#0-4) 

### Recommendation
Add a zero-address check in the `EvmHost` constructor mirroring `HostManager`'s pattern:
```solidity
constructor(address _admin) {
    if (_admin == address(0)) revert InvalidAdmin();
    _consensusUpdateTimestamp = block.timestamp;
    _hostParams.admin = _admin;
}
```
Additionally, consider validating `params.admin != address(0)` inside `updateHostParamsInternal` so that a future cross-chain `UpdateParams` governance action cannot zero out the admin either.

### Proof of Concept
1. Deploy `EvmHost` (or `TestnetHost`) with `admin = address(0)` — no revert occurs since the constructor performs no validation: [6](#0-5) 
2. Any account attempts `host.initialize(params)`. `_msgSender()` is never `address(0)`, so `_msgSender() != _hostParams.admin` is always true, and the call always reverts with `UnauthorizedAction`. [7](#0-6) 
3. `_initialized` never becomes `true`, `hostManager`/`handler`/`consensusClient` remain `address(0)` forever, and there is no path (governance or otherwise) to recover the host, since governance actions must be delivered through this same host.

### Citations

**File:** evm/src/core/EvmHost.sol (L359-369)
```text
    /**
     * @dev Constructor only sets the initial admin and the consensus update
     * timestamp. All other configuration is deferred to `initialize` so that
     * the constructor's init code is identical on every chain (assuming the
     * same `admin` is used everywhere), which is required for CREATE2 address
     * parity across chains.
     */
    constructor(address _admin) {
        _consensusUpdateTimestamp = block.timestamp;
        _hostParams.admin = _admin;
    }
```

**File:** evm/src/core/EvmHost.sol (L371-381)
```text
    /**
     * @dev One-shot initializer. Can only be called once, and only by the
     * admin set in the constructor. Applies the initial `HostParams` via
     * the internal updater.
     */
    function initialize(HostParams memory params) external {
        if (_msgSender() != _hostParams.admin) revert UnauthorizedAction();
        if (_initialized) revert UnauthorizedAction();
        _initialized = true;
        updateHostParamsInternal(params);
    }
```

**File:** evm/src/core/EvmHost.sol (L581-636)
```text
    function updateHostParamsInternal(HostParams memory params) internal {
        // check the params to prevent the host from getting bricked.
        if (
            params.hostManager == address(0) || address(params.hostManager).code.length == 0
                || !IERC165(params.hostManager).supportsInterface(type(IApp).interfaceId)
        ) {
            // otherwise cannot process new cross-chain governance requests
            revert InvalidHostManager();
        }

        if (
            params.handler == address(0) || address(params.handler).code.length == 0
                || !IERC165(params.handler).supportsInterface(type(IHandlerV2).interfaceId)
        ) {
            // otherwise cannot process new datagrams
            revert InvalidHandler();
        }

        if (
            params.consensusClient == address(0) || address(params.consensusClient).code.length == 0
                || !IERC165(params.consensusClient).supportsInterface(type(IConsensusV2).interfaceId)
        ) {
            // otherwise cannot process new consensus datagrams
            revert InvalidConsensusClient();
        }

        // otherwise cannot process new cross-chain governance requests
        if (keccak256(params.hyperbridge) == keccak256(bytes(""))) revert InvalidHyperbridgeId();

        // otherwise cannot process new datagrams
        uint256 stateMachinesLen = params.stateMachines.length;
        if (stateMachinesLen == 0) revert InvalidStateMachinesLength();

        // otherwise cannot process new datagrams
        if (1 days > params.unStakingPeriod) revert InvalidUnstakingPeriod();

        address oldFeeToken = feeToken();
        if (oldFeeToken != address(0) && oldFeeToken != params.feeToken) {
            uint256 balance = IERC20(oldFeeToken).balanceOf(address(this));
            if (balance != 0) revert CannotChangeFeeToken();
        }

        // safe to emit here because invariants have already been checked
        // and don't want to store a temp variable for the old params
        emit HostParamsUpdated({oldParams: _hostParams, newParams: params});

        _hostParams.feeToken = params.feeToken;
        _hostParams.admin = params.admin;
        _hostParams.handler = params.handler;
        _hostParams.hostManager = params.hostManager;
        _hostParams.uniswapV2 = params.uniswapV2;
        _hostParams.unStakingPeriod = params.unStakingPeriod;
        _hostParams.challengePeriod = params.challengePeriod;
        _hostParams.consensusClient = params.consensusClient;
        _hostParams.stateMachines = params.stateMachines;
        _hostParams.hyperbridge = params.hyperbridge;
```

**File:** evm/src/core/HostManager.sol (L61-81)
```text
    // @dev The admin may not be zero. It is the only account able to deliver governance here, so
    // a zero admin would leave no way to reach this contract again, rotation included.
    error InvalidAdmin();

    /**
     * @dev Emitted when a `SetAdmin` request replaces the admin
     * @param previous The admin before this change
     * @param current The admin from now on
     */
    event AdminUpdated(address previous, address current);

    // @dev restricts call to the provided `caller`
    modifier restrict(address who, address caller) {
        if (who != caller) revert UnauthorizedAction();
        _;
    }

    constructor(HostManagerParams memory managerParams) {
        if (managerParams.admin == address(0)) revert InvalidAdmin();
        _params = managerParams;
    }
```

**File:** evm/script/DeployIsmp.s.sol (L115-140)
```text
        EvmHost host = isMainnet
            ? new EvmHost{salt: salt}(admin)
            : EvmHost(payable(address(new TestnetHost{salt: salt}(admin))));
        // Host manager. Its admin is the only relayer whose governance deliveries it accepts; a
        // `SetAdmin` request from Hyperbridge rotates it later.
        HostManager manager = new HostManager{salt: salt}(
            HostManagerParams({admin: vm.envAddress("GOVERNANCE_RELAYER"), host: address(host)})
        );
        uint256[] memory stateMachines = new uint256[](1);
        stateMachines[0] = paraId;

        // EvmHost
        HostParams memory params = HostParams({
            uniswapV2: uniswapV2,
            admin: admin,
            hostManager: address(manager),
            handler: address(handler),
            unStakingPeriod: 21 * (60 * 60 * 24),
            challengePeriod: 0,
            consensusClient: address(consensusClient),
            hyperbridge: hyperbridge,
            feeToken: feeToken,
            stateMachines: stateMachines
        });

        host.initialize(params);
```
