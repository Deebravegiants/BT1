### Title
Native-token dispatch payment permanently breaks if `feeToken` is set to WETH - ([File: evm/src/core/EvmHost.sol])

### Summary
`EvmHost.dispatch()`, `dispatch(DispatchGet)`, and `fundRequest()` all convert `msg.value` (native ETH) into the configured `feeToken` by calling `IUniswapV2Router02.swapETHForExactTokens` with a hard-coded path `[WETH, feeToken()]`. If governance ever sets `feeToken` to WETH itself, this path degenerates to `[WETH, WETH]`, which Uniswap V2 rejects (`IDENTICAL_ADDRESSES`), permanently reverting every native-payment dispatch call.

### Finding Description
`HostParams.feeToken` is documented as intentionally configurable ("This will typically be DAI. but we allow it to be configurable to prevent future regrets") and `updateHostParamsInternal` validates the handler, consensus client, host manager, hyperbridge id, unstaking period, and state-machine list, but never validates the relationship between `feeToken` and the native wrapped asset (`IUniswapV2Router02(uniswapV2).WETH()`): [1](#0-0) 

Every native-payment code path builds a two-hop swap path where `path[0]` is always the router's WETH and `path[1]` is `feeToken()`: [2](#0-1) [3](#0-2) [4](#0-3) 

If `feeToken() == IUniswapV2Router02(uniswapV2).WETH()`, then `path = [WETH, WETH]`. `swapETHForExactTokens` internally calls `UniswapV2Library.getAmountsIn`, which calls `pairFor`/`sortTokens` and reverts with `IDENTICAL_ADDRESSES` because there is no WETH/WETH pool — exactly the same root cause as the referenced report, where a Uniswap pool always prices a token against WETH and therefore cannot price WETH against itself.

### Impact Explanation
This makes it impossible for any unprivileged user to dispatch a `PostRequest`/`GetRequest` or fund an existing request using native ETH whenever the host's `feeToken` is WETH — every such call reverts. Since the fee-token field is explicitly designed to be arbitrary/configurable (per the code comment) and the update function performs no compatibility check against the native asset, a legitimate governance configuration silently and permanently disables the native-payment dispatch route for the entire host, forcing all users to hold and pre-approve the ERC20 feeToken directly. This matches the "route unable to deliver messages" impact class for message dispatch.

### Likelihood Explanation
Requires only a single, plausible governance parameter update (`updateHostParams`/cross-chain `SetHostParam`) setting `feeToken` to the chain's WETH address — a configuration the codebase's own comment states is intentionally supported ("we allow it to be configurable to prevent future regrets") and which is not rejected by any of the existing validation checks in `updateHostParamsInternal`. Once set, the break is triggered by every subsequent unprivileged `dispatch`/`fundRequest` call using `msg.value`.

### Recommendation
In `updateHostParamsInternal`, reject configurations where `params.feeToken == IUniswapV2Router02(params.uniswapV2).WETH()` (or more generally, verify a swap path/pool exists between the native wrapped asset and the new fee token before accepting the update). Alternatively, in the dispatch/fundRequest native-payment branches, special-case `feeToken() == WETH` by wrapping ETH directly via `IWETH.deposit{value: msg.value}()` instead of routing through the Uniswap swap.

### Proof of Concept
1. Governance calls `updateHostParams`/delivers a `SetHostParam` governance request setting `feeToken = WETH_ADDRESS` (allowed since no check prevents it — see `evm/src/core/EvmHost.sol:581-636`).
2. Any user calls `host.dispatch{value: X}(DispatchPost{...})`.
3. Inside `dispatch`, `path = [router.WETH(), feeToken()]` resolves to `[WETH, WETH]`, and `router.swapETHForExactTokens` reverts with `UniswapV2Library: IDENTICAL_ADDRESSES`.
4. Every native-value call to `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest` now permanently reverts until governance rolls back `feeToken`.

### Citations

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

**File:** evm/src/core/EvmHost.sol (L921-932)
```text
    function dispatch(DispatchPost memory post) external payable notFrozen returns (bytes32 commitment) {
        if (msg.value > 0) {
            address[] memory path = new address[](2);
            address uniswapV2 = _hostParams.uniswapV2;
            path[0] = IUniswapV2Router02(uniswapV2).WETH();
            path[1] = feeToken();
            IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
                post.fee, path, address(this), block.timestamp
            );
        } else if (post.fee > 0) {
            IERC20(feeToken()).safeTransferFrom(_msgSender(), address(this), post.fee);
        }
```

**File:** evm/src/core/EvmHost.sol (L974-985)
```text
    function dispatch(DispatchGet memory get) external payable notFrozen returns (bytes32 commitment) {
        if (msg.value > 0) {
            address[] memory path = new address[](2);
            address uniswapV2 = _hostParams.uniswapV2;
            path[0] = IUniswapV2Router02(uniswapV2).WETH();
            path[1] = feeToken();
            IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
                get.fee, path, address(this), block.timestamp
            );
        } else if (get.fee > 0) {
            IERC20(feeToken()).safeTransferFrom(_msgSender(), address(this), get.fee);
        }
```

**File:** evm/src/core/EvmHost.sol (L1031-1042)
```text
    function fundRequest(bytes32 commitment, uint256 amount) external payable notFrozen {
        if (msg.value > 0) {
            address[] memory path = new address[](2);
            address uniswapV2 = _hostParams.uniswapV2;
            path[0] = IUniswapV2Router02(uniswapV2).WETH();
            path[1] = feeToken();
            IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
                amount, path, address(this), block.timestamp
            );
        } else {
            IERC20(feeToken()).safeTransferFrom(_msgSender(), address(this), amount);
        }
```
