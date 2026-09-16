Confirmed pattern is identical across both `WrappedHyperFungibleToken.sol` and `WrappedHyperFungibleTokenUpgradeable.sol`. This is the strongest analog reachable by an unprivileged sender/relayer in the token-bridge mint/burn path.

### Title
Missing zero-address validation on `beneficiary`/`refundee` in `WrappedHyperFungibleToken(Upgradeable).onAccept`/`onPostRequestTimeout` permanently burns native ETH - (File: `sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol`, `sdk/packages/core/contracts/apps/WrappedHyperFungibleTokenUpgradeable.sol`)

### Summary
The `_toAddr` helper only validates that the encoded recipient bytes are exactly 20 bytes long; it never rejects the all-zero encoding that decodes to `address(0)`. In the `isWeth` branch of `onAccept` and `onPostRequestTimeout`, the derived `beneficiary`/`refundee` is used directly as the target of a native ETH `.call{value: ...}("")`. A low-level call with value sent to `address(0)` succeeds (there is no receiver-side revert), so ETH delivered to that address is unrecoverable, mirroring the missing `to != address(0)` check flagged in the external report's `update` function.

### Finding Description
`_toAddr` in both `WrappedHyperFungibleToken.sol` and `WrappedHyperFungibleTokenUpgradeable.sol` only checks `b.length != 20`: [1](#0-0) 

`onAccept` decodes `message.to` (fully controlled by the caller of `send()` on the source chain via `params.to`) into `beneficiary` and, in the WETH branch, pushes native ETH straight to it without an `address(0)` guard: [2](#0-1) 

The same pattern exists for `refundee` in `onPostRequestTimeout`, and identically in the non-upgradeable `WrappedHyperFungibleToken.sol`: [3](#0-2) 

`send()` places `params.to` verbatim into the dispatched `Message.to` field with no validation: [4](#0-3) 

Because `address(0).call{value: amount}("")` always returns `sent == true` (an empty call to any address with no code succeeds), the fallback re-wrap-and-ERC20-transfer safety path (added specifically to avoid "permanently lock[ing] funds", per the code's own comment) never triggers for a zero recipient. The ETH is unwrapped from WETH and irreversibly sent to `address(0)`, permanently destroying it.

### Impact Explanation
Native ETH unwrapped for delivery to a zero-encoded recipient is permanently and irrecoverably lost — a direct instance of the "permanent freezing of funds" outcome accepted by the scope rules. Because `onAccept`'s WETH branch first calls `IWETH(_underlying).withdraw(message.amount)`, converting locked WETH into native ETH before the doomed push, the funds are destroyed rather than merely stuck in the contract, unlike the ERC20 branch where `safeTransfer(address(0), amount)` would revert under standards-compliant tokens.

### Likelihood Explanation
Likelihood is high: any user who calls `send()` with `params.to` equal to 20 zero bytes (accidentally, e.g. from an unset/uninitialized recipient variable off-chain, or due to any encoding bug on the caller's tooling) triggers the loss with no possible recovery, exactly matching the "Low impact / High likelihood" profile of the source report. No relayer or admin privilege is required — a single ordinary bridging transaction suffices to reach the vulnerable path.

### Recommendation
Add an explicit zero-address check on the decoded recipient in both `onAccept` and `onPostRequestTimeout` before the native-ETH push (and before the ERC20 fallback), reverting or routing to a safe recovery address instead of silently completing the transfer to `address(0)`:
```solidity
function _toAddr(bytes memory b) internal pure returns (address addr) {
    if (b.length != 20) revert InvalidAddress(b.length);
    addr = address(bytes20(b));
    if (addr == address(0)) revert InvalidAddress(0);
}
```

### Proof of Concept
1. Caller invokes `send()` on the wrapped-WETH deployment with `params.to = bytes20(address(0))` and a valid `amount`. [5](#0-4) 
2. The ISMP request is relayed and delivered on the destination chain; the host calls `onAccept`.
3. `beneficiary = _toAddr(message.to)` resolves to `address(0)`; since `_isWeth` is true, `IWETH(_underlying).withdraw(message.amount)` converts the locked WETH into native ETH held by the contract.
4. `beneficiary.call{value: message.amount}("")` executes against `address(0)` and returns `sent == true`, so the re-wrap fallback never runs.
5. `message.amount` of native ETH is now held by nobody — permanently unrecoverable — while the corresponding WETH escrow on the source chain has already been debited from the sender.

### Citations

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleTokenUpgradeable.sol (L264-281)
```text
        bytes memory body = abi.encode(
            HyperFungibleTokenUpgradeable.Message({
                from: abi.encodePacked(msg.sender),
                to: params.to,
                amount: params.amount,
                data: params.data
            })
        );

        return DispatchPost({
            dest: params.dest,
            to: dest,
            body: body,
            timeout: params.timeout,
            fee: params.relayerFee,
            payer: msg.sender
        });
    }
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleTokenUpgradeable.sol (L294-318)
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

        emit Sent({
            from: msg.sender,
            to: params.to,
            dest: string(params.dest),
            amount: params.amount,
            commitment: commitment
        });
    }
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleTokenUpgradeable.sol (L336-350)
```text
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
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleTokenUpgradeable.sol (L395-401)
```text
    /// @notice Extracts an address from the first 20 bytes of a bytes memory value
    function _toAddr(bytes memory b) internal pure returns (address addr) {
        if (b.length != 20) revert InvalidAddress(b.length);
        // casting to 'bytes20' is safe because we already checked length
        // forge-lint: disable-next-line(unsafe-typecast)
        return address(bytes20(b));
    }
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L299-336)
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

        if (message.data.length > 0) {
            ICallDispatcher(_dispatcher).dispatch(message.data);
        }

        emit Received({
            from: message.from,
            to: beneficiary,
            source: string(request.source),
            amount: message.amount
        });
    }
```
