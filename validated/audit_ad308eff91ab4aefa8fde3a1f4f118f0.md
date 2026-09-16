### Title
Permanent freezing of escrowed funds when the underlying token has a blocklist (e.g. USDC) — `WrappedHyperFungibleToken` unconditionally calls `safeTransfer`/`safeTransferFrom` on delivery and timeout refund - (File: `sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol`)

### Summary
`WrappedHyperFungibleToken` locks an arbitrary underlying ERC20 (its docs and tests explicitly reference wrapping tokens like USDC) on the source chain and unlocks it on the destination chain via `onAccept`, with a refund path via `onPostRequestTimeout`. Both paths perform a direct `safeTransfer` to an address decoded from the cross-chain message with no fallback, no try/catch, and no admin rescue mechanism. If the underlying token enforces a blocklist (as USDC's `blacklister` role does), and either the destination beneficiary or the original sender becomes blocklisted, the corresponding transfer reverts unconditionally and permanently.

### Finding Description
`send()` locks tokens with `IERC20(_underlying).safeTransferFrom(msg.sender, address(this), params.amount)` [1](#0-0) .

On delivery, `onAccept` decodes the beneficiary from the message body and unconditionally calls `IERC20(_underlying).safeTransfer(beneficiary, message.amount)` for non-WETH underlyings [2](#0-1) .

If the request never delivers (because the beneficiary is on the underlying token's blocklist and every relayer attempt to call `onAccept` reverts) the request eventually times out, and `onPostRequestTimeout` attempts to refund the original sender with the same unconditional `safeTransfer` call and no fallback: [3](#0-2) .

Unlike the WETH branch, which explicitly has fallback logic to avoid permanently locking funds when a native-ETH push fails ("so the refund path doesn't permanently lock funds for the same caller class"), the plain-ERC20 branch has no such protection [4](#0-3) . There is no owner/admin rescue function anywhere in the contract to redirect funds to an alternate address if both the beneficiary and the refund path are unreachable.

This mirrors the reported analog exactly: the L2StandardBridge report flags that the bridge's own documentation/description does not account for ERC20 tokens with a blocklist (e.g. USDC), which can cause transfers to permanently revert for a blocklisted address. `WrappedHyperFungibleToken` is designed to wrap arbitrary existing ERC20 tokens (per its own NatSpec: "Cross-chain wrapper for existing ERC20 tokens") [5](#0-4) , and the SDK/Token Governor documentation confirms USDC-class tokens are intended targets ("MYTOKEN", multi-chain wrapped USDC examples appear throughout the HFT docs) [6](#0-5) .

### Impact Explanation
If the destination beneficiary address specified in a cross-chain transfer is blocklisted on the underlying token (whether pre-existing, or blocklisted after the message is dispatched but before it's delivered — e.g. sanctioned addresses, compromised accounts, or malicious actors deliberately routing funds to a soon-to-be-blocklisted address), delivery via `onAccept` will always revert. The message can never be delivered, and once it times out, the refund attempt in `onPostRequestTimeout` also transfers to a fixed decoded address (`message.from`, the original sender) with no fallback. If that sender address is itself later blocklisted (plausible for the same category of accounts), the refund also reverts unconditionally and repeatedly. Since there is no rescue/sweep function in the contract, the escrowed underlying tokens become permanently locked in the `WrappedHyperFungibleToken` contract with no recovery path — a direct loss of funds for the affected user and a stuck balance for the protocol.

### Likelihood Explanation
Medium likelihood: it requires the underlying wrapped token to implement a blocklist (true for USDC and other centrally-administered stablecoins, which are prime candidates for wrapping via this exact contract) and for either the beneficiary or the sender address to be or become blocklisted. This is a realistic and externally-triggerable condition (regulatory/compliance blocklisting is routine for USDC), not an attacker-controlled admin/governance action, so it fits the "unprivileged token bridger" reachable path.

### Recommendation
- Wrap the destination `safeTransfer` (and the timeout refund `safeTransfer`) in a try/catch, similar to the existing WETH fallback pattern, and on failure escrow the funds under a claimable mapping keyed by the intended beneficiary/refundee rather than reverting the whole `onAccept`/`onPostRequestTimeout` call.
- Add an owner-gated (or beneficiary-gated) rescue/redirect function allowing a blocklisted recipient to nominate an alternate, non-blocklisted address to claim escrowed funds.
- Document explicitly (as the original L2StandardBridge report recommended) that this contract does not safely support underlying tokens with blocklist/freeze functionality, or add pre-flight blocklist checks where feasible (e.g. via `isBlacklisted` interface checks for USDC-like tokens) before locking funds in `send()`.

### Proof of Concept
1. Deploy `WrappedHyperFungibleToken` on chain A configured with `_underlying = USDC`.
2. User calls `send()` with `params.to` = address `R`, locking USDC in the contract [1](#0-0) .
3. Before the message is relayed and delivered on chain B, USDC's blacklister blocklists `R` (or `R` was already blocklisted, e.g. a sanctioned address).
4. Every relayer attempt to call `onAccept` on chain B's `WrappedHyperFungibleToken` reverts at `IERC20(_underlying).safeTransfer(beneficiary, message.amount)` [7](#0-6) , so the message can never be delivered.
5. Once the request's timeout elapses, a relayer submits the timeout proof and `onPostRequestTimeout` is invoked on chain A, attempting to refund the original sender via `IERC20(_underlying).safeTransfer(refundee, message.amount)` [8](#0-7) . If the sender is also blocklisted (or later becomes blocklisted before the timeout fires), this call reverts too, and the tokens remain stuck in the contract indefinitely with no way to recover them.

### Citations

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L32-47)
```text
/**
 * @title WrappedHyperFungibleToken
 * @author Polytope Labs (hello@polytope.technology)
 * @notice Cross-chain wrapper for existing ERC20 tokens.
 * Locks the underlying token on the source chain and mints/unlocks on the destination chain.
 *
 * @dev Inherits HyperApp for cross-chain message handling and Ownable for configuration.
 * The owner configures which chains this wrapper can communicate with, the address of the
 * corresponding deployment on each chain, and the underlying ERC20 token.
 *
 * Also supports native token wrapping: if isWeth is true during send, the
 * contract wraps the native token by treating the underlying ERC20 as WETH.
 *
 * Supports optional calldata execution on the destination chain via CallDispatcher,
 * enabling composable cross-chain interactions (e.g., transfer-and-swap).
 */
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

**File:** docs/content/developers/evm/hyper-fungible-token/hyper-fungible-token.mdx (L24-26)
```text
bytes32 salt = keccak256("my-token-v1");
HyperFungibleToken token = new HyperFungibleToken{salt: salt}("Wrapped USDC", "wUSDC", msg.sender);
```
```
