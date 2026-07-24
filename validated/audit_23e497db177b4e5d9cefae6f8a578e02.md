### Title
Unregistered ERC1155 Token Accepted by `initTransfer1155` Causes Irreversible Fund Lock - (File: evm/src/omni-bridge/contracts/OmniBridge.sol)

### Summary
`initTransfer1155` accepts and locks any ERC1155 token without verifying that the token has been registered via `logMetadata1155`. Because the NEAR-side `fin_transfer_callback` hard-panics when it cannot find decimals for the unregistered deterministic address, the locked ERC1155 tokens can never be released, and no admin rescue path exists in the contract.

### Finding Description
The intended ERC1155 onboarding flow requires a prior call to `logMetadata1155(tokenAddress, tokenId)`, which populates `multiTokens[deterministicToken]` on the EVM side and emits a `LogMetadata` event that triggers NEAR-side token registration (including `token_decimals` insertion). Only after that registration is complete can a round-trip transfer succeed.

`initTransfer1155` performs no such check:

```solidity
function initTransfer1155(
    address tokenAddress,
    uint256 tokenId,
    ...
) external payable whenNotPaused(PAUSED_INIT_TRANSFER) {
    currentOriginNonce += 1;
    if (fee >= amount) { revert InvalidFee(); }

    address deterministicToken = deriveDeterministicAddress(tokenAddress, tokenId);

    IERC1155(tokenAddress).safeTransferFrom(   // ← tokens locked here
        msg.sender, address(this), tokenId, amount, ""
    );
    // ← no check: multiTokens[deterministicToken].tokenAddress != address(0)
    ...
    emit BridgeTypes.InitTransfer(...);
}
``` [1](#0-0) 

The EVM bridge locks the tokens and emits `InitTransfer` with `deterministicToken` as the token address. When a relayer submits the resulting proof to NEAR's `fin_transfer_callback`, the callback immediately hard-panics:

```rust
let decimals = self
    .token_decimals
    .get(&init_transfer.token)
    .near_expect(BridgeError::TokenDecimalsNotFound);
``` [2](#0-1) 

Because `deterministicToken` was never registered, `token_decimals` has no entry for it. The NEAR transaction reverts, the `InitTransfer` event is never finalized, and the ERC1155 tokens remain permanently locked in the EVM bridge. `OmniBridge.sol` contains no admin sweep or rescue function for ERC1155 tokens.

The test suite itself demonstrates the missing guard: the "validates ERC1155 receiver hooks" test calls `initTransfer1155` without any prior `logMetadata1155` call and the call succeeds, confirming the contract imposes no registration requirement. [3](#0-2) 

### Impact Explanation
Any user who calls `initTransfer1155` with an ERC1155 token that has not been registered via `logMetadata1155` will have their tokens permanently locked in the EVM bridge with no recovery path. This matches the **Critical** impact category: irreversible fund lock / permanently unclaimable user value in bridge flows.

### Likelihood Explanation
The function is public and unpermissioned. A user who is unaware of the required pre-registration step, or who races ahead of the `logMetadata1155` call, will trigger the lock. The `logMetadata1155` function is also public and unpermissioned, so there is no enforced ordering between the two calls. Likelihood is **Medium-High**: the path requires no special privilege and is reachable by any token holder with ERC1155 approval set.

### Recommendation
Add an existence check at the top of `initTransfer1155` before accepting any tokens:

```solidity
function initTransfer1155(
    address tokenAddress,
    uint256 tokenId,
    ...
) external payable whenNotPaused(PAUSED_INIT_TRANSFER) {
    address deterministicToken = deriveDeterministicAddress(tokenAddress, tokenId);
    require(
        multiTokens[deterministicToken].tokenAddress != address(0),
        "ERR_TOKEN_NOT_REGISTERED"
    );
    ...
}
```

This mirrors the pattern already used in `finTransfer`, where `multiToken.tokenAddress != address(0)` gates the ERC1155 release path. [4](#0-3) 

### Proof of Concept
1. Deploy any ERC1155 contract and mint tokens to attacker address.
2. Approve `OmniBridge` as operator.
3. Call `OmniBridge.initTransfer1155(erc1155Address, tokenId, amount, 0, 0, "victim.near", "")` — **without** any prior `logMetadata1155` call.
4. Observe: `safeTransferFrom` succeeds, tokens are now held by the bridge, `InitTransfer` event is emitted.
5. Relayer submits the proof to NEAR `fin_transfer`.
6. NEAR `fin_transfer_callback` panics with `ERR_TOKEN_DECIMALS_NOT_FOUND`.
7. Tokens remain locked in the EVM bridge permanently; no admin function exists to recover them. [5](#0-4) [2](#0-1)

### Citations

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L323-330)
```text
        } else if (multiToken.tokenAddress != address(0)) {
            IERC1155(multiToken.tokenAddress).safeTransferFrom(
                address(this),
                payload.recipient,
                multiToken.tokenId,
                payload.amount,
                ""
            );
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

**File:** near/omni-bridge/src/lib.rs (L719-722)
```rust
        let decimals = self
            .token_decimals
            .get(&init_transfer.token)
            .near_expect(BridgeError::TokenDecimalsNotFound);
```

**File:** evm/tests/OmniBridge1155.test.ts (L191-194)
```typescript
    await bridge
      .connect(user)
      .initTransfer1155(await erc1155.getAddress(), tokenId, 1, 0, 0, "receiver.near", "")
    expect(await erc1155.balanceOf(bridgeAddress, tokenId)).to.equal(1n)
```
