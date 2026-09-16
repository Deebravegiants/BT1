### Title
`WrappedHyperFungibleToken` custody address can be blacklisted by censorable underlying tokens (e.g. USDC), permanently freezing all locked funds and breaking the bridge - (File: `sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol`)

### Summary
`WrappedHyperFungibleToken` (and its upgradeable variant) is designed to wrap arbitrary ERC20 tokens, locking the underlying asset in the contract itself on the source chain and releasing it via `safeTransfer` on the destination/refund path. If the configured `underlying` token supports an address-level freeze/blacklist (as USDC's `FiatTokenV2` does — the exact class of token cited in the referenced HGTRemote report), the contract address itself can become blacklisted, causing every `safeTransferFrom`/`safeTransfer` call against it to revert. This is architecturally identical to the reported `HGTRemote` issue: a single dedicated bridge contract holding custody of a blacklist-capable ERC20.

### Finding Description
`send()` pulls the underlying token into the contract's own balance via `safeTransferFrom(msg.sender, address(this), params.amount)`: [1](#0-0) 

`onAccept()` (delivery of an incoming cross-chain transfer) and `onPostRequestTimeout()` (refund of a locked-but-undelivered transfer) both release funds by calling `safeTransfer` directly from the contract's own balance to the beneficiary/refundee: [2](#0-1) [3](#0-2) 

The contract deployment address for `WrappedHyperFungibleToken` is fixed once deployed (e.g. via CREATE2, per the HFT deployment docs) and is registered as a peer on every remote chain. If the token issuer (Circle for USDC, or any other issuer with a blacklist function, e.g. USDT) blacklists this contract's address — whether due to it having received tainted funds routed through it by a malicious user, regulatory action, or an operational mistake — every subsequent `safeTransferFrom` (locking new deposits) and `safeTransfer` (releasing locked funds on delivery or timeout refund) will revert, because the underlying token's `transfer`/`transferFrom` implementation blocks any transfer to or from the blacklisted address.

Since the wrapper holds custody of all locked underlying tokens for that trading pair/route, a blacklist event freezes:
1. All tokens already locked in the contract awaiting delivery on the destination chain (their beneficiaries can no longer receive them via `onAccept`).
2. All tokens in-flight that would be refunded on timeout via `onPostRequestTimeout`.
3. All future `send()` calls attempting to lock new deposits.

This mirrors the exact root cause in the external report: a single non-upgradeable custody address is exposed to token-level censorship with no fallback recovery path (no alternate withdrawal address, no owner-controlled rescue mechanism visible in this contract).

### Impact Explanation
Any censorable ERC20 (USDC being the most widely used one) configured as the `underlying` for a `WrappedHyperFungibleToken` deployment turns that entire bridge route into a single point of failure. A blacklist event — triggerable by an unprivileged attacker simply routing OFAC-sanctioned or otherwise flagged funds through the bridge to get the contract's own custody address flagged — permanently freezes all already-locked user funds (no way to release via `onAccept` or refund via `onPostRequestTimeout`) and makes the bridge route nonfunctional going forward. This is a concrete, permanent freezing-of-funds condition for the affected token bridge instance.

### Likelihood Explanation
Likelihood is directly proportional to which underlying token is configured — this is a design-level exposure that materializes whenever the underlying token supports issuer-level blacklisting (USDC, USDT, and similar centrally-issued stablecoins are the primary candidates and the most likely tokens to be bridged given liquidity demand). No governance or admin misbehavior is required; a single malicious counterparty sending sanctioned/flagged funds through the wrapper, or an issuer proactively freezing addresses associated with mixers/hacks, is sufficient to trigger blacklisting of the pooled custody address, exactly as described in the referenced audit finding.

### Recommendation
- Avoid using a single shared custody contract address for censorable tokens; consider per-transfer escrow sub-accounts, or a pull-based release pattern where the destination `onAccept` mints/authorizes a claim rather than directly holding and pushing the underlying asset.
- Add an owner/governance-controlled emergency migration path that can move custody to a fresh, non-blacklisted contract address and re-point in-flight commitments to it.
- Document the blacklist risk explicitly for integrators choosing which ERC20 to configure as `underlying`, and discourage use of centrally-blacklistable stablecoins without a mitigation plan.

### Proof of Concept
1. Deploy `WrappedHyperFungibleToken` with `underlying = USDC` on chain A (source) and its peer on chain B (destination), per the standard configuration flow.
2. User A calls `send()`, which locks USDC into the wrapper via `safeTransferFrom` (`WrappedHyperFungibleToken.sol:272`).
3. Before the message is delivered on chain B, or before a timeout refund is processed on chain A, USDC's issuer blacklists the wrapper contract's address on chain A (e.g., because a different user sent sanctioned funds through the same contract, or due to any other blacklist trigger).
4. `onAccept`/`onPostRequestTimeout` calls that would `safeTransfer` locked USDC out of the contract (`WrappedHyperFungibleToken.sol:323`, `:361`) now revert unconditionally because USDC's `transfer` function checks the sender is not blacklisted.
5. All USDC locked in the wrapper is permanently frozen; the bridge route becomes nonfunctional for that token, matching the impact described in the referenced `HGTRemote` finding.

### Citations

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
