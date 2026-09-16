### Title
Compromised/malicious owner can permanently pause cross-chain token bridge and LayerZero endpoint contracts, then renounce ownership to brick them forever - ([File: sdk/packages/core/contracts/apps/HyperFungibleToken.sol])

### Summary
`HyperFungibleToken`, `HyperFungibleTokenUpgradeable`, `WrappedHyperFungibleToken`, `WrappedHyperFungibleTokenUpgradeable`, and `HyperbridgeLzEndpoint` all inherit OpenZeppelin's `Ownable`/`OwnableUpgradeable` together with `Pausable`/`PausableUpgradeable`, expose `pause()`/`unpause()` as `onlyOwner`, and gate their core bridging entry points with `whenNotPaused`. None of these contracts override `renounceOwnership()`. A compromised or malicious owner can call `pause()` and then `renounceOwnership()`, leaving the contract permanently paused with no account able to call `unpause()` ever again.

### Finding Description
Each of these token-bridge / message-relay applications defines:
```solidity
function pause() external onlyOwner { _pause(); }
function unpause() external onlyOwner { _unpause(); }
``` [1](#0-0) [2](#0-1) 

and the core cross-chain functions require `whenNotPaused`:
```solidity
function send(SendParams calldata params) external payable whenNotPaused { ... }
``` [3](#0-2) 
```solidity
function onPostRequestTimeout(...) public virtual override onlyHost whenNotPaused { ... }
``` [4](#0-3) 
```solidity
function send(...) external payable override whenNotPaused returns (MessagingReceipt memory) { ... }
``` [5](#0-4) 

These contracts inherit `Ownable`/`OwnableUpgradeable` directly with no override of `renounceOwnership()`: [6](#0-5) [7](#0-6) [8](#0-7) [9](#0-8) [10](#0-9) [11](#0-10) [12](#0-11) 

A grep across the repository confirms `renounceOwnership` is never referenced or overridden in any of these bridge/token contract files — the only occurrences elsewhere are in unrelated deployment scripts, an unrelated JSON ABI, and generated TS ABI bindings, none of which disable/override the function for these contracts.

Since `Ownable.renounceOwnership()` is `public virtual` and unguarded beyond `onlyOwner`, any owner (legitimate or compromised via a leaked key) can:
1. Call `pause()` — freezing `send()` on the token/endpoint, and freezing `onPostRequestTimeout` refunds.
2. Call `renounceOwnership()` — setting the owner to `address(0)`.

After this, `unpause()` is permanently uncallable by anyone, since the `onlyOwner` modifier will never match `address(0)`.

### Impact Explanation
This permanently freezes:
- Outgoing cross-chain transfers via `send()` on `HyperFungibleToken`/`HyperFungibleTokenUpgradeable`/`WrappedHyperFungibleToken`/`WrappedHyperFungibleTokenUpgradeable` and `HyperbridgeLzEndpoint`.
- Refund minting via `onPostRequestTimeout()`, meaning any tokens burned on the source chain for in-flight transfers that later time out can never be re-minted back to the sender — a permanent, unrecoverable loss of user funds.
- All ERC20 `transfer`/`transferFrom` on `HyperFungibleToken`, which are also gated `whenNotPaused`.
- All LayerZero-routed messaging through `HyperbridgeLzEndpoint`, breaking any OApp relying on it for cross-chain messaging permanently.

This qualifies as permanent freezing of funds/route unable to deliver messages, satisfying the required impact bar.

### Likelihood Explanation
Requires the contract owner's key to be compromised or the owner to act maliciously — the same precondition as the original Footium report. Given these are production bridge/token contracts controlling live user funds in transit, a compromised owner key is a realistic threat model already assumed by the protocol's own admin/pause design (the pause feature exists precisely to react to incidents, e.g., a compromised owner using it maliciously against the protocol itself). No additional privilege beyond existing ownership is needed to permanently brick the contract.

### Recommendation
Override `renounceOwnership()` in `HyperFungibleToken`, `HyperFungibleTokenUpgradeable`, `WrappedHyperFungibleToken`, `WrappedHyperFungibleTokenUpgradeable`, and `HyperbridgeLzEndpoint` to disable it (revert unconditionally), or require transferring ownership to a valid non-zero multisig/timelock instead of allowing renouncement while paused. Alternatively, use a two-step ownership transfer/timelocked admin recovery mechanism and disallow `renounceOwnership()` entirely for contracts holding user funds in transit.

### Proof of Concept
1. Owner calls `HyperFungibleToken.pause()` — sets `_paused = true`, blocking `send()`, `transfer()`, `transferFrom()`, and `onPostRequestTimeout()`.
2. Owner calls `renounceOwnership()` (inherited, unoverridden) — sets owner to `address(0)`.
3. Any subsequent call to `unpause()` reverts because `onlyOwner` can never be satisfied again.
4. Any user whose burned tokens are awaiting a timeout refund via `onPostRequestTimeout` (or awaiting delivery) permanently loses access to those funds, and the bridge is bricked for all future transfers.

### Citations

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L16-21)
```text
import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
import {Pausable} from "@openzeppelin/contracts/utils/Pausable.sol";
import {ERC165} from "@openzeppelin/contracts/utils/introspection/ERC165.sol";
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L44-45)
```text
contract HyperFungibleToken is ERC20, ERC165, HyperApp, Ownable, Pausable {
    using SafeERC20 for IERC20;
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L209-223)
```text
    /**
     * @notice Pauses all cross-chain operations (send and receive)
     * @dev Only callable by the contract owner
     */
    function pause() external onlyOwner {
        _pause();
    }

    /**
     * @notice Unpauses all cross-chain operations
     * @dev Only callable by the contract owner
     */
    function unpause() external onlyOwner {
        _unpause();
    }
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L264-270)
```text
    function send(SendParams calldata params) external payable whenNotPaused {
        _burn(msg.sender, params.amount);
        DispatchPost memory request = _buildDispatchPost(params);

        bytes32 commitment;
        if (msg.value > 0) {
            commitment = IDispatcher(_host).dispatch{value: msg.value}(request);
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

**File:** sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol (L16-17)
```text
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
import {Pausable} from "@openzeppelin/contracts/utils/Pausable.sol";
```

**File:** sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol (L51-51)
```text
contract HyperbridgeLzEndpoint is HyperApp, Ownable, Pausable, ILayerZeroEndpointV2 {
```

**File:** sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol (L243-257)
```text
    /**
     * @notice Pauses all cross-chain operations (send and receive)
     * @dev Only callable by the contract owner
     */
    function pause() external onlyOwner {
        _pause();
    }

    /**
     * @notice Unpauses all cross-chain operations
     * @dev Only callable by the contract owner
     */
    function unpause() external onlyOwner {
        _unpause();
    }
```

**File:** sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol (L261-265)
```text
    /// @inheritdoc ILayerZeroEndpointV2
    function send(
        MessagingParams calldata _params,
        address /* _refundAddress */
    ) external payable override whenNotPaused returns (MessagingReceipt memory) {
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleTokenUpgradeable.sol (L45-52)
```text
contract HyperFungibleTokenUpgradeable is
    Initializable,
    ERC20Upgradeable,
    ERC165Upgradeable,
    HyperApp,
    OwnableUpgradeable,
    PausableUpgradeable
{
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L16-20)
```text
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
import {Pausable} from "@openzeppelin/contracts/utils/Pausable.sol";
import {ERC165} from "@openzeppelin/contracts/utils/introspection/ERC165.sol";
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L48-49)
```text
contract WrappedHyperFungibleToken is ERC165, HyperApp, Ownable, Pausable {
    using SafeERC20 for IERC20;
```
