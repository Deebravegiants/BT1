### Title
`send()` burns tokens before validating the destination `to` address, permanently losing funds if it decodes to `address(0)` - (File: `sdk/packages/core/contracts/apps/HyperFungibleToken.sol`)

### Summary
`HyperFungibleToken.send()` unconditionally burns the caller's tokens via `_burn(msg.sender, params.amount)` at [1](#0-0)  before any validation of the `params.to` recipient bytes. The recipient is only decoded to an address later, on the destination chain, inside `onAccept` via `_toAddr(message.to)` [2](#0-1) , which is then passed straight to `_mint(beneficiary, message.amount)` [3](#0-2) . Neither `send()` nor `onAccept`/`_toAddr` reject a zero address.

### Finding Description
This mirrors the reported bug class exactly: an irreversible state change (burn/escrow-debit) happens before validating the user-supplied receiver, and no downstream step can recover from a receiver mistake.

- `_toAddr` only validates the byte length (must be 20 bytes) — it does not reject the all-zero address: [4](#0-3) 
- `onAccept` mints directly to the decoded `beneficiary` with no zero-address check: [5](#0-4) 
- The same pattern exists in the upgradeable variant's `onAccept`: [6](#0-5) 

Because `params.to` is arbitrary user-supplied `bytes` (not constrained to be non-zero, and not even guaranteed to encode a real EVM address for EVM destinations), a user who fat-fingers the recipient (e.g., passes `abi.encodePacked(address(0))`, an empty value that pads to zero, or any other value that decodes to `address(0)`) has their source-chain balance burned immediately and irrevocably. If the message is delivered successfully, `_mint` sends the newly minted supply to `address(0)`, permanently destroying the value — the user cannot claim/retry/re-target the recipient, unlike the timeout path (which correctly refunds the original sender via `onPostRequestTimeout`, `_mint(refundee, message.amount)` at [7](#0-6) , but that only fires if the message actually times out, not on successful delivery).

This is directly analogous to the original report's `SolverVaultToken.burnFrom` prior to `receiver` validation in `requestWithdraw` — burn-then-validate is the identical anti-pattern, and here it also spans a cross-chain hop, so there is no on-chain path (like `claimForWithdrawRequest`) to intercept or cancel the transfer once dispatched.

### Impact Explanation
Loss is permanent and equals the full bridged amount for any affected transfer: tokens are burned on the source chain and (on successful delivery) minted to `address(0)` on the destination, with no recovery mechanism. This satisfies "concrete theft or permanent freezing of funds" — funds are destroyed, not merely locked. Given `HyperFungibleToken`/`BridgeToken` and the upgradeable variant are the standard cross-chain fungible-token bridging contracts intended for wide external use (see `BridgeToken.sol`, the native Hyperbridge token bridge [8](#0-7) ), this affects any unprivileged end user calling `send()` directly or through an integrating wallet/SDK that fails to validate the recipient before submission.

### Likelihood Explanation
Reachable by any single unprivileged transaction — a normal user calling `send()` with a malformed/zero recipient. The report's exact human-error scenario (copy-paste error, wrong padding of a 20-byte address into 32 bytes on the Substrate side, or template code defaulting to zero) is entirely plausible, especially since `to` is raw `bytes` accepted without format/zero checks. However, likelihood is somewhat tempered by the fact that a competent SDK layer might validate addresses before constructing the call (uncertain — the on-chain contract itself provides no protection, and any direct contract caller or a buggy client integration is fully exposed).

### Recommendation
Add an explicit check that `params.to` decodes to a non-zero address (and, ideally, is exactly 20 bytes for EVM destinations) in `send()`/`_buildDispatchPost` before burning, e.g.:
```solidity
address recipient = _toAddr(params.to); // or a non-reverting variant that checks length
if (recipient == address(0)) revert InvalidRecipient();
```
Perform the same check defensively in `onAccept` before minting, so that even if a malformed message somehow reaches this stage, tokens are not minted to `address(0)` (revert or hold in an escrow account for governance-recoverable refund instead of silent burn).

### Proof of Concept
1. User calls `HyperFungibleToken.send()` with `params.to = abi.encodePacked(address(0))` (or bytes that pad to zero) and a valid `params.amount`.
2. `_burn(msg.sender, params.amount)` executes immediately, debiting the user's balance [1](#0-0) .
3. The ISMP POST request is dispatched and, assuming normal relayer delivery (no timeout), is delivered to the destination chain.
4. Destination `onAccept` decodes `message.to` via `_toAddr` to `address(0)` and calls `_mint(address(0), message.amount)` [2](#0-1) .
5. Tokens are permanently destroyed: the user's source-chain balance is gone, and no equivalent balance exists anywhere reachable by any account.

### Citations

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L264-266)
```text
    function send(SendParams calldata params) external payable whenNotPaused {
        _burn(msg.sender, params.amount);
        DispatchPost memory request = _buildDispatchPost(params);
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L292-301)
```text
    function onAccept(IncomingPostRequest calldata incoming) public virtual override onlyHost whenNotPaused {
        PostRequest calldata request = incoming.request;

        bytes memory expectedSource = _supportedChains[request.source];
        if (expectedSource.length == 0) revert UnsupportedChain();
        if (keccak256(request.from) != keccak256(expectedSource)) revert UnauthorizedSource();

        Message memory message = abi.decode(request.body, (Message));
        address beneficiary = _toAddr(message.to);
        _mint(beneficiary, message.amount);
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L321-326)
```text
    function onPostRequestTimeout(PostRequestTimeout memory incoming) public virtual override onlyHost whenNotPaused {
        Message memory message = abi.decode(incoming.request.body, (Message));
        address refundee = _toAddr(message.from);
        _mint(refundee, message.amount);
        emit Refunded({to: refundee, amount: message.amount});
    }
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L328-334)
```text
    /// @notice Extracts an address from the first 20 bytes of a bytes memory value
    function _toAddr(bytes memory b) internal pure returns (address addr) {
        if (b.length != 20) revert InvalidAddress(b.length);
        // casting to 'bytes20' is safe because we already checked length
        // forge-lint: disable-next-line(unsafe-typecast)
        return address(bytes20(b));
    }
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleTokenUpgradeable.sol (L320-330)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost whenNotPaused {
        PostRequest calldata request = incoming.request;

        bytes memory expectedSource = _supportedChains[request.source];
        if (expectedSource.length == 0) revert UnsupportedChain();
        if (keccak256(request.from) != keccak256(expectedSource)) revert UnauthorizedSource();

        Message memory message = abi.decode(request.body, (Message));
        address beneficiary = _toAddr(message.to);
        _mint(beneficiary, message.amount);

```

**File:** evm/src/apps/BridgeToken.sol (L21-37)
```text
/**
 * @title BridgeToken
 * @author Polytope Labs (hello@polytope.technology)
 * @notice The EVM representation of BRIDGE, the native token of the nexus parachain.
 *
 * @dev BRIDGE is native to nexus, so the two ends run the escrow model: `pallet-hyper-fungible-token`
 * escrows the native balance on nexus and this contract mints the equivalent here, meaning the supply
 * of this token is always backed by the pallet's escrow account. Sending back burns here and releases
 * there.
 *
 * Metadata and the nexus peer are fixed in the bytecode rather than passed at deployment, so every
 * chain gets an identical token, and with CREATE2 an identical address for the same deployer and salt.
 *
 * `decimals()` is the inherited ERC20 default of 18 while BRIDGE is 12 decimals on nexus, so the
 * pallet scales by 10^6 in both directions. The chain config registered on nexus via `register_token`
 * must therefore declare 18 decimals for this contract.
 */
```
