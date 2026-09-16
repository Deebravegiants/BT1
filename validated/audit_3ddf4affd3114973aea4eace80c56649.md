## Title
`WrappedHyperFungibleToken.send()` does not account for fee-on-transfer/deflationary underlying tokens, allowing unbacked cross-chain mint/unlock and depletion of the locked-token reserve - (File: `sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol`)

### Summary
`WrappedHyperFungibleToken.send()` pulls the underlying ERC20 via `safeTransferFrom(msg.sender, address(this), params.amount)` and then dispatches a cross-chain `Message` that commits to the full, unreduced `params.amount` as the amount to be minted/unlocked on the destination chain. If the underlying token charges a transfer fee (deflationary/fee-on-transfer token), the contract actually receives less than `params.amount`, but the destination chain still mints or unlocks the full requested amount, creating an accounting mismatch between escrowed collateral and outstanding cross-chain liabilities.

### Finding Description
In `send()`: [1](#0-0) 

the contract calls `IERC20(_underlying).safeTransferFrom(msg.sender, address(this), params.amount)` and, without measuring the actual balance change, builds the `DispatchPost` body from the caller-supplied `params.amount` via `_buildDispatchPost`: [2](#0-1) 

This is the same root cause identified in the referenced report — using the pre-transfer parameter as the recorded/committed amount instead of measuring the post-transfer balance delta. The `IntentGatewayV2` contracts in this same repo already implement the correct mitigation (balance-before/after diffing) for exactly this class of bug: [3](#0-2) 

but `WrappedHyperFungibleToken.send()` was not updated with the same protection.

On the receiving side, the peer contract trusts `message.amount` unconditionally and either mints (`HyperFungibleToken.onAccept`) or unlocks/transfers the underlying (`WrappedHyperFungibleToken.onAccept`) the full committed amount: [4](#0-3) [5](#0-4) 

Because the home-chain wrapper actually escrowed less than `params.amount` (due to the transfer fee), every send under-collateralizes the outstanding cross-chain supply by the fee amount. Repeated sends accumulate a growing shortfall between the wrapper's actual `_underlying` balance and the total amount owed to holders of the minted/bridged representation on remote chains.

### Impact Explanation
This is a single-transaction-reachable accounting bug in a token bridge mint/burn (lock/unlock) path. Each `send()` call with a fee-on-transfer underlying token results in an unbacked over-issuance on the destination chain equal to the transfer fee. Over time (or with a single large transfer of a high-fee token), the home-chain `WrappedHyperFungibleToken`'s underlying balance becomes insufficient to honor all outstanding unlock/timeout-refund obligations, i.e., the last users to bridge back or the last timeout refund to be processed will find `IERC20(_underlying).safeTransfer` reverting due to insufficient balance — a permanent freezing of funds for those users, and an unbacked-mint condition on the remote chain in the interim.

### Likelihood Explanation
Likelihood depends on the owner configuring `_underlying` to a fee-on-transfer/deflationary token, which is plausible for a generic "wrap any existing ERC20" bridge design; the contract makes no assumption restricting `_underlying` to standard, fee-free tokens, and no on-chain check enforces that assumption. Any user calling `send()` on such a deployment triggers the mismatch with no special privileges required.

### Recommendation
In `send()`, measure the actual amount received by diffing `IERC20(_underlying).balanceOf(address(this))` before and after `safeTransferFrom`, and use that measured amount (not `params.amount`) when building the `Message`/`DispatchPost` body, mirroring the fix already applied in `IntentGatewayV2.sol`. Alternatively, explicitly document and enforce (e.g., via a check against expected balance delta) that `_underlying` must not be a fee-on-transfer token, reverting otherwise.

### Proof of Concept
1. Owner configures `WrappedHyperFungibleToken` with `_underlying` = a token that deducts a 1% fee on every `transfer`/`transferFrom` (e.g., the `FeeOnTransferToken` mock already present in the test suite: [6](#0-5) ).
2. A user calls `send({ amount: 1000e18, ... })`. `safeTransferFrom` moves `1000e18` requested but the contract only receives `990e18` due to the 1% fee.
3. `_buildDispatchPost` still encodes `amount: 1000e18` into the `Message`, which is dispatched cross-chain.
4. On the destination chain, `HyperFungibleToken.onAccept` mints `1000e18` to the beneficiary — 10e18 more than what is actually backed by the `990e18` locked on the home chain.
5. If the beneficiary later bridges back (or the message times out and a refund on the home chain is issued for `1000e18`), `WrappedHyperFungibleToken.onAccept`/`onPostRequestTimeout` attempts to `safeTransfer` `1000e18` of `_underlying`, but the contract holds only `990e18` (minus fees from other operations), causing a revert and permanently freezing that user's redemption once accumulated shortfalls exceed the actual balance.

### Citations

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

**File:** evm/src/apps/IntentGatewayV2.sol (L312-323)
```text
        } else {
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                if (token == address(0)) {
                    if (msgValue < order.inputs[i].amount) revert InsufficientNativeToken();
                    msgValue -= order.inputs[i].amount;
                } else {
                    uint256 balBefore = IERC20(token).balanceOf(address(this));
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                    order.inputs[i].amount = IERC20(token).balanceOf(address(this)) - balBefore;
                }
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L292-313)
```text
    function onAccept(IncomingPostRequest calldata incoming) public virtual override onlyHost whenNotPaused {
        PostRequest calldata request = incoming.request;

        bytes memory expectedSource = _supportedChains[request.source];
        if (expectedSource.length == 0) revert UnsupportedChain();
        if (keccak256(request.from) != keccak256(expectedSource)) revert UnauthorizedSource();

        Message memory message = abi.decode(request.body, (Message));
        address beneficiary = _toAddr(message.to);
        _mint(beneficiary, message.amount);

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

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L2701-2735)
```text
        feeBps = _feeBps;
    }

    function mint(address to, uint256 amount) external {
        balanceOf[to] += amount;
        totalSupply += amount;
    }

    function approve(address spender, uint256 amount) external returns (bool) {
        allowance[msg.sender][spender] = amount;
        return true;
    }

    function transfer(address to, uint256 amount) external returns (bool) {
        return _transfer(msg.sender, to, amount);
    }

    function transferFrom(address from, address to, uint256 amount) external returns (bool) {
        uint256 allowed = allowance[from][msg.sender];
        if (allowed != type(uint256).max) {
            allowance[from][msg.sender] = allowed - amount;
        }
        return _transfer(from, to, amount);
    }

    function _transfer(address from, address to, uint256 amount) internal returns (bool) {
        uint256 fee = (amount * feeBps) / 10_000;
        uint256 received = amount - fee;
        balanceOf[from] -= amount;
        balanceOf[to] += received;
        // fee is burned
        totalSupply -= fee;
        return true;
    }
}
```
