### Title
`WrappedHyperFungibleToken.send()` silently pulls WETH from users when insufficient native ETH is sent, without reverting - (File: `sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol`)

### Summary
`WrappedHyperFungibleToken.send()` (and the identical logic in `WrappedHyperFungibleTokenUpgradeable.sol`) is meant to let users pay for a cross-chain transfer either fully in native ETH (WETH mode) or fully in the underlying ERC20 (WETH pulled via allowance). When `_isWeth == true` but the caller sends less native ETH than `params.amount`, the function does not revert — it silently falls into the ERC20 pull branch and drains the *full* `params.amount` of WETH from the caller via `safeTransferFrom`, while still forwarding the caller's non-zero (but insufficient) `msg.value` onward as a native fee payment to `EvmHost.dispatch`. This mirrors the exact bug class in the referenced Napier `TrancheRouter.issue()` report: an ambiguous native/ERC20 payment branch with no consistency check, silently pulling ERC20 tokens the user did not intend to spend in that flow.

### Finding Description
In `send()`: [1](#0-0) 

```solidity
function send(HyperFungibleToken.SendParams calldata params) external payable whenNotPaused {
    uint256 msgValue = msg.value;
    if (_isWeth && msgValue >= params.amount) {
        msgValue = msgValue - params.amount;
        IWETH(_underlying).deposit{value: params.amount}();
    } else {
        IERC20(_underlying).safeTransferFrom(msg.sender, address(this), params.amount);
    }

    DispatchPost memory request = _buildDispatchPost(params);
    bytes32 commitment;
    if (msgValue > 0) {
        commitment = IDispatcher(_host).dispatch{value: msgValue}(request);
    } else {
        commitment = dispatchWithFeeToken(request);
    }
    ...
```

The branch selection only checks `_isWeth && msgValue >= params.amount`. There is no explicit revert for the inconsistent case where `_isWeth == true` and `0 < msgValue < params.amount`. In that case:
1. The `else` branch fires and pulls the **entire** `params.amount` of the underlying WETH from `msg.sender` via `safeTransferFrom` — relying on a pre-existing ERC20 allowance, which is common for periphery/bridge contracts that support both native and ERC20 payment modes (the docs themselves describe both an ERC20 approval flow and a native flow for the very same `send()` function).
2. `msgValue` is never zeroed out in the `else` branch (unlike the `if` branch), so the leftover native ETH the user sent is still forwarded via `IDispatcher(_host).dispatch{value: msgValue}(request)`, silently being spent as a native relayer-fee payment via `EvmHost.dispatch`'s Uniswap swap path. [2](#0-1) 

The user's intended flow (pay `params.amount` fully in native ETH, wrapped via WETH) silently degrades into paying the full `params.amount` in ERC20 WETH via allowance **and** additionally having their sent native ETH consumed for fee payment — with no revert warning them that the native amount sent was insufficient for the mode they configured. This is the same root-cause pattern as the audited `TrancheRouter.issue()` bug: a missing consistency check between `msg.value` and the intended payment mode, allowing silent unintended pulls from user token balances.

### Impact Explanation
Any unprivileged caller of `send()` who has an outstanding WETH allowance to this contract (a realistic and even encouraged setup, since the same contract supports pure-ERC20 mode requiring pre-approval) can have significantly more value extracted from them than intended if they (or their wallet/dApp integration) send an amount of native ETH smaller than `params.amount`. Because there is no revert, the failure is silent: the full WETH amount is pulled from the depositor via allowance while their under-provided ETH is simultaneously spent on fees, resulting in loss of assets for the affected user with no refund path. This satisfies "concrete theft ... of funds" for message-dispatching users of this in-scope periphery contract.

### Likelihood Explanation
The trigger condition only requires a single external call to `send()` with `msg.value` set below `params.amount` while `_isWeth` is enabled and the caller carries a WETH allowance — no privileged role, admin action, or off-chain infrastructure is needed. Wallets and SDK integrations that mis-estimate `nativeFee + amount` (a documented two-part calculation: `msg.value = amount + nativeFee`) can trivially hit this path, and it is also directly exploitable by any user/integrator who reuses a max-approval WETH allowance against this contract.

### Recommendation
Add an explicit consistency check mirroring the fix pattern already applied by industry precedent (`PeripheryPayments._pay`'s WETH check): when `_isWeth` is true and the caller supplies a non-zero `msg.value` insufficient to cover `params.amount`, revert instead of silently falling back to the ERC20 pull path.

```solidity
function send(HyperFungibleToken.SendParams calldata params) external payable whenNotPaused {
    uint256 msgValue = msg.value;
    if (_isWeth && msgValue >= params.amount) {
        msgValue = msgValue - params.amount;
        IWETH(_underlying).deposit{value: params.amount}();
    } else {
        if (_isWeth && msgValue > 0) revert InsufficientNativeToken();
        IERC20(_underlying).safeTransferFrom(msg.sender, address(this), params.amount);
    }
    ...
```

Apply the identical fix to `WrappedHyperFungibleTokenUpgradeable.sol`, which contains the same logic. [3](#0-2) 

### Proof of Concept
1. Owner configures `WrappedHyperFungibleToken` with `isWeth = true` and `underlying = WETH`.
2. Alice previously approves `type(uint256).max` WETH allowance to the wrapper contract (e.g. from prior interactions, or standard wallet UX for bridge contracts).
3. Alice intends to bridge `1 ether` and calls `send{value: 0.5 ether}(params)` where `params.amount = 1 ether` — either due to a fee-estimation bug in her client, or a malicious dApp front-end.
4. `_isWeth && msgValue >= params.amount` is `false` (0.5 < 1), so the `else` branch executes: `IERC20(WETH).safeTransferFrom(alice, address(this), 1 ether)` pulls the full 1 WETH from Alice.
5. `msgValue` remains `0.5 ether` (never zeroed), so `IDispatcher(_host).dispatch{value: 0.5 ether}(request)` is called, spending Alice's leftover native ETH on the fee swap in `EvmHost.dispatch`.
6. Result: Alice loses 1 full WETH via allowance plus 0.5 ETH in fee payment, without any revert warning her that her `msg.value` was inconsistent with the WETH-mode payment she intended — analogous to the Napier `TrancheRouter.issue()` loss-of-funds scenario.

### Citations

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L266-281)
```text
    function send(HyperFungibleToken.SendParams calldata params) external payable whenNotPaused {
        uint256 msgValue = msg.value;
        if (_isWeth && msgValue >= params.amount) {
            msgValue = msgValue - params.amount;
            IWETH(_underlying).deposit{value: params.amount}();
        } else {
            IERC20(_underlying).safeTransferFrom(msg.sender, address(this), params.amount);
        }

        DispatchPost memory request = _buildDispatchPost(params);
        bytes32 commitment;
        if (msgValue > 0) {
            commitment = IDispatcher(_host).dispatch{value: msgValue}(request);
        } else {
            commitment = dispatchWithFeeToken(request);
        }
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

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleTokenUpgradeable.sol (L294-309)
```text
    function send(HyperFungibleTokenUpgradeable.SendParams calldata params) external payable whenNotPaused {
        uint256 msgValue = msg.value;
        if (_isWeth && msgValue >= params.amount) {
            msgValue = msgValue - params.amount;
            IWETH(_underlying).deposit{value: params.amount}();
        } else {
            IERC20(_underlying).safeTransferFrom(msg.sender, address(this), params.amount);
        }

        DispatchPost memory request = _buildDispatchPost(params);
        bytes32 commitment;
        if (msgValue > 0) {
            commitment = IDispatcher(_host).dispatch{value: msgValue}(request);
        } else {
            commitment = dispatchWithFeeToken(request);
        }
```
