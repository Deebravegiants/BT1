This is a valid analog. The `IntentGatewayV2.sol` contract explicitly handles fee-on-transfer tokens by measuring actual balance changes (as shown in the code and dedicated tests: [1](#0-0) ), but `WrappedHyperFungibleToken.sol`, a lock/unlock cross-chain bridge for arbitrary ERC20 tokens, does not apply the same protection.

### Title
WrappedHyperFungibleToken.send locks a fee-on-transfer token's post-fee balance but dispatches the pre-fee `params.amount` to be unlocked/minted on the destination chain - (File: sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol)

### Summary
`WrappedHyperFungibleToken.send()` calls `IERC20(_underlying).safeTransferFrom(msg.sender, address(this), params.amount)` and then unconditionally builds the cross-chain `Message` with `amount: params.amount` — the amount the user requested, not the amount actually received by the contract.

### Finding Description
In the ERC20 (non-WETH) branch of `send()`: [2](#0-1) 
the contract does not measure `balanceOf(address(this))` before and after the transfer to determine the actual amount locked. It instead trusts `params.amount` and embeds it directly into the dispatched `Message.amount` via `_buildDispatchPost`: [3](#0-2) 

If `_underlying` is a fee-on-transfer token (or one that may add such a fee in the future, e.g. USDT-style upgradeable fee mechanisms), the contract's actual token balance increases by less than `params.amount`. On the destination chain, `onAccept` unlocks/transfers out `message.amount` (the full pre-fee amount) to the beneficiary: [4](#0-3) 

This is the same root cause as the referenced Taurus finding: the contract assumes `amountRequested == amountReceived` for a token transfer that can silently deduct a fee, and propagates the requested (not actual) amount into downstream accounting — here, into a cross-chain unlock instruction rather than a collateral ledger.

By contrast, the same repository's `IntentGatewayV2.sol` correctly guards against this exact issue by snapshotting balances before/after `safeTransferFrom` and using the delta as the escrowed/committed amount, with explicit fee-on-transfer test coverage (`testPlaceOrder_FeeOnTransferToken_EscrowMatchesReceived`, etc.), confirming the team is aware of this bug class but did not apply the fix to `WrappedHyperFungibleToken`.

### Impact Explanation
Each cross-chain transfer of a fee-on-transfer underlying token locks `params.amount - fee` but commits the peer contract to release `params.amount`. Over repeated transfers, the peer-side pool of locked underlying tokens becomes under-collateralized relative to the cumulative amounts promised in dispatched messages. Eventually, unlocks for legitimate users will revert due to insufficient balance (`safeTransfer` failure) — a permanent freezing of funds for whichever transfer exhausts the shortfall — or, if the contract holds excess balance from other transfers, an early unlock can drain funds meant to back subsequent transfers, effectively enabling one user's action to cause a shortfall that harms other users' bridged funds. This is a direct backing/insolvency bug in a token bridge, reachable by any single unprivileged `send()` call using a fee-on-transfer or fee-capable ERC20 as `_underlying`.

### Likelihood Explanation
Likelihood depends on `_underlying` being (or becoming) a fee-on-transfer/deflationary token, which the owner selects at `configure()` time. Given real-world tokens like PAXG, STA, and upgradeable-fee tokens like USDT/USDC exist, and `WrappedHyperFungibleToken` is a generic wrapper meant to support "existing ERC20 tokens," this is a realistic deployment configuration, not a purely theoretical one.

### Recommendation
Mirror the pattern already used in `IntentGatewayV2.sol`: snapshot `IERC20(_underlying).balanceOf(address(this))` immediately before and after `safeTransferFrom` in `send()`, and use the actual received delta (not `params.amount`) as `message.amount` in the dispatched `Message`/`DispatchPost`.

### Proof of Concept
1. Owner configures `WrappedHyperFungibleToken` with `_underlying` set to a token that charges a 1% transfer fee (or later upgrades to add one).
2. User calls `send({dest, to, amount: 1000e18, ...})`.
3. `safeTransferFrom` moves 1000e18 requested but the contract's balance only increases by 990e18 due to the fee.
4. `_buildDispatchPost` still encodes `amount: 1000e18` in the `Message` body and dispatches it.
5. On the destination chain's `onAccept`, `IERC20(_underlying).safeTransfer(beneficiary, 1000e18)` is attempted/emitted as owed, exceeding what was actually locked on the source chain by 10e18, creating a shortfall in the bridge's backing that manifests as failed unlocks or fund freezing for later transfers.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L320-323)
```text
                    uint256 balBefore = IERC20(token).balanceOf(address(this));
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                    order.inputs[i].amount = IERC20(token).balanceOf(address(this)) - balBefore;
                }
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L234-253)
```text
    function _buildDispatchPost(HyperFungibleToken.SendParams calldata params) internal view returns (DispatchPost memory) {
        bytes memory dest = _supportedChains[params.dest];
        if (dest.length == 0) revert UnsupportedChain();

        bytes memory body = abi.encode(HyperFungibleToken.Message({
            from: abi.encodePacked(msg.sender),
            to: params.to,
            amount: params.amount,
            data: params.data
        }));

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

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L266-290)
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

        emit Sent({
            from: msg.sender,
            to: params.to,
            dest: string(params.dest),
            amount: params.amount,
            commitment: commitment
        });
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
