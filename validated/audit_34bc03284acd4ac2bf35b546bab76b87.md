## Analog Found: `WrappedHyperFungibleToken.configure()` can strand escrowed funds by reassigning `_underlying`

### Title
Reconfiguring `_underlying` in `WrappedHyperFungibleToken`/`WrappedHyperFungibleTokenUpgradeable` strands previously escrowed tokens - (File: `sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol`)

### Summary
`configure()` lets the owner change the wrapper's `_underlying` ERC20 address at any time, with no restriction analogous to the set-once guard applied to `_host`. Every fund-moving function (`send`, `onAccept`, `onPostRequestTimeout`) operates exclusively against whatever `_underlying` is currently set. If the owner repoints `_underlying` after users have already locked tokens of the old underlying via `send()`, the contract's balance of that old token becomes permanently unreachable: no function in the contract references any token other than the live `_underlying`.

### Finding Description
`send()` custodies user funds by pulling the configured underlying token into the contract: [1](#0-0) 

`configure()` allows the owner to overwrite `_underlying` unconditionally — only `_host` is guarded as set-once: [2](#0-1) 

Delivery of an incoming cross-chain message (`onAccept`) and timeout refunds (`onPostRequestTimeout`) both transfer out of `_underlying` — the one currently configured, not the one that was in effect when the corresponding `send()` locked funds: [3](#0-2) [4](#0-3) 

Because the contract keeps no per-token accounting and every withdrawal path (`onAccept`, `onPostRequestTimeout`) is hardcoded to `_underlying`, any balance of a previously configured underlying token sitting in the contract when `configure()` is called with a new `underlying` address is orphaned — there is no function that can move it out. This is structurally identical to the reported Union Finance bug class: an admin-writable address (here `_underlying`, there `userManagers[token]`) is used both to receive/escrow funds and to gate/execute their later release, and updating that address does not migrate or protect funds already escrowed under the old value. The identical pattern exists in the upgradeable variant: [5](#0-4) 

### Impact Explanation
Any tokens locked in the wrapper under a previously configured `_underlying` become permanently stranded once the owner reconfigures the wrapper to a different underlying token — a concrete, permanent freezing of user funds with no recovery path in the contract. This is a Medium-severity fund-freezing bug matching the reported bug class.

### Likelihood Explanation
`configure()` is a normal, expected operational lever (used, per the constructor/config docs, to (re)point the wrapper at host/dispatcher/underlying), not requiring any malicious behavior — an operator swapping a token implementation (e.g. migrating a stablecoin, fixing an initial misconfiguration, or repointing to a WETH variant) while `send()`-originated deposits are outstanding is a realistic operational scenario, exactly like the original Union report's non-malicious admin action.

### Recommendation
Guard `_underlying` similarly to `_host` (set-once, or require the contract's balance of the current `_underlying` to be zero before allowing a change), or version escrows by underlying token address so in-flight funds under a prior underlying remain redeemable after reconfiguration.

### Proof of Concept
1. Owner deploys and configures `WrappedHyperFungibleToken` with `underlying = TokenA`.
2. User calls `send()`, locking `TokenA` into the contract (see `send()` at lines 266-273).
3. Owner calls `configure()` again with `underlying = TokenB` (lines 178-185) — no restriction prevents this while `TokenA` balance is nonzero.
4. Any subsequent `onAccept()` or `onPostRequestTimeout()` for the earlier `TokenA`-based message will attempt to move `TokenB` (lines 299-324, 344-365), and the escrowed `TokenA` balance can never be swept out by any function in the contract, since none references any token other than the live `_underlying`.

### Citations

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L178-185)
```text
    function configure(WrappedConfigOptions calldata options) external onlyOwner {
        if (_host == address(0)) {
            _host = options.host;
        }
        _dispatcher = options.dispatcher;
        _underlying = options.underlying;
        _isWeth = options.isWeth;
    }
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L266-273)
```text
    function send(HyperFungibleToken.SendParams calldata params) external payable whenNotPaused {
        uint256 msgValue = msg.value;
        if (_isWeth && msgValue >= params.amount) {
            msgValue = msgValue - params.amount;
            IWETH(_underlying).deposit{value: params.amount}();
        } else {
            IERC20(_underlying).safeTransferFrom(msg.sender, address(this), params.amount);
        }
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L299-324)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost whenNotPaused {
        PostRequest calldata request = incoming.request;

        bytes memory expectedSource = _supportedChains[request.source];
        if (expectedSource.length == 0) revert UnsupportedChain();
        if (keccak256(request.from) != keccak256(expectedSource)) revert UnauthorizedSource();

        HyperFungibleToken.Message memory message = abi.decode(request.body, (HyperFungibleToken.Message));
        address beneficiary = _toAddr(message.to);

        if (_isWeth) {
            // Try a native-ETH push first (cheap for EOAs and payable contracts);
            // if the recipient cannot accept native value (no `receive()` / `fallback()
            // payable`), re-wrap the withdrawn ETH and deliver the underlying WETH as
            // an ERC-20 transfer instead. This mirrors the deposit-side flexibility of
            // `send()` (which accepts WETH from non-payable callers via `safeTransferFrom`)
            // so the refund path doesn't permanently lock funds for the same caller class.
            IWETH(_underlying).withdraw(message.amount);
            (bool sent,) = beneficiary.call{value: message.amount}("");
            if (!sent) {
                IWETH(_underlying).deposit{value: message.amount}();
                IERC20(_underlying).safeTransfer(beneficiary, message.amount);
            }
        } else {
            IERC20(_underlying).safeTransfer(beneficiary, message.amount);
        }
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L344-365)
```text
    function onPostRequestTimeout(PostRequestTimeout calldata incoming) external override onlyHost whenNotPaused {
        HyperFungibleToken.Message memory message = abi.decode(incoming.request.body, (HyperFungibleToken.Message));
        address refundee = _toAddr(message.from);

        if (_isWeth) {
            // Try a native-ETH push first; if the refundee cannot accept native value
            // (e.g. the caller used the ERC-20 deposit path in `send()` from a
            // non-payable contract), re-wrap the withdrawn ETH and deliver the
            // underlying WETH as an ERC-20 transfer so the timeout still settles and
            // funds are not permanently locked.
            IWETH(_underlying).withdraw(message.amount);
            (bool sent,) = refundee.call{value: message.amount}("");
            if (!sent) {
                IWETH(_underlying).deposit{value: message.amount}();
                IERC20(_underlying).safeTransfer(refundee, message.amount);
            }
        } else {
            IERC20(_underlying).safeTransfer(refundee, message.amount);
        }

        emit Refunded({to: refundee, amount: message.amount});
    }
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleTokenUpgradeable.sol (L200-207)
```text
    function configure(WrappedConfigOptions calldata options) external onlyOwner {
        if (_host == address(0)) {
            _host = options.host;
        }
        _dispatcher = options.dispatcher;
        _underlying = options.underlying;
        _isWeth = options.isWeth;
    }
```
