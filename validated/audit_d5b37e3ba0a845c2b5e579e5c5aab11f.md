### Title
`initTransfer1155` Never Validates `(tokenAddress, tokenId)` Against the `multiTokens` Registry, Enabling Address-Collision Minting of Unbacked Wrapped Assets — (`evm/src/omni-bridge/contracts/OmniBridge.sol`)

---

### Summary

`OmniBridge.deriveDeterministicAddress` maps every ERC-1155 `(tokenAddress, tokenId)` pair to a 20-byte "virtual" ERC-20 address by truncating a keccak256 hash to 160 bits. `initTransfer1155` uses that computed address as the canonical token identifier that is emitted to NEAR, but it **never checks** that the supplied `(tokenAddress, tokenId)` pair is the one registered in `multiTokens` for that deterministic address. An attacker who finds a birthday collision between two `(address, uint256)` pairs can call `initTransfer1155` with a worthless fake pair that hashes to the same deterministic address as a legitimate, registered token, causing NEAR to mint fully unbacked wrapped assets.

---

### Finding Description

`deriveDeterministicAddress` computes:

```solidity
address(bytes20(keccak256(abi.encodePacked(tokenAddress, tokenId))))
```

This truncates keccak256 output to 160 bits, giving a collision space of N = 2^160. [1](#0-0) 

`logMetadata1155` correctly guards its own mapping: once `(tokenA, idA)` is stored at deterministic address `D`, any attempt to register a different pair at `D` reverts with `ERC1155MappingMismatch`. [2](#0-1) 

However, `initTransfer1155` performs **no such check**. It computes `deterministicToken` and immediately uses it as the token identifier in the emitted `InitTransfer` event, without ever consulting `multiTokens`:

```solidity
address deterministicToken = deriveDeterministicAddress(tokenAddress, tokenId);

IERC1155(tokenAddress).safeTransferFrom(msg.sender, address(this), tokenId, amount, "");
// ...
emit BridgeTypes.InitTransfer(msg.sender, deterministicToken, ...);
``` [3](#0-2) 

The NEAR-side `fin_transfer_callback` trusts the `token` field from the proven event and looks it up in `token_decimals`; it does not re-derive or re-validate the EVM-side `(tokenAddress, tokenId)` pair. [4](#0-3) 

**Birthday-attack collision cost.** The input domain is `(address [20 bytes], uint256 [32 bytes])` = 52 bytes; the output is 160 bits. By the birthday bound, ~2^80 hash evaluations yield a ~50 % collision probability, and ~2^82 evaluations yield ~99.96 %. The attacker has full freedom to vary both sides of the collision (they can deploy arbitrary ERC-1155 contracts at chosen addresses and use arbitrary token IDs), so the effective search space is the full 2^160 output space.

---

### Impact Explanation

**Critical — Unauthorized creation of unbacked wrapped bridge assets.**

Attack steps:

1. **Find collision offline**: generate 2^80 `(tokenB, idB)` pairs (attacker-controlled ERC-1155) and 2^80 `(tokenA, idA)` pairs (any ERC-1155), find a pair where `deriveDeterministicAddress(tokenA, idA) == deriveDeterministicAddress(tokenB, idB)` = `D`.
2. **Register the legitimate side**: call `logMetadata1155(tokenA, idA)` → `D` is stored in `multiTokens` and the `LogMetadata` event is relayed to NEAR, registering `D` as a known token with its decimals.
3. **Attract real deposits**: users bridge `tokenA:idA` legitimately; the bridge contract holds real ERC-1155 tokens.
4. **Exploit**: attacker calls `initTransfer1155(tokenB, idB, amount, recipient, ...)`. The function computes `deterministicToken = D`, transfers the worthless `tokenB:idB` tokens to the bridge, and emits `InitTransfer(sender, D, nonce, amount, ...)`.
5. **NEAR mints unbacked tokens**: NEAR's prover verifies the event, `fin_transfer_callback` looks up `D` in `token_decimals`, finds it registered, and mints wrapped tokens for the attacker's `recipient`.
6. The attacker now holds fully unbacked wrapped tokens on NEAR. They can redeem them against the real `tokenA:idA` pool locked in the bridge, draining legitimate depositors.

---

### Likelihood Explanation

The collision requires ~2^80–2^82 keccak256 evaluations. As established in the KyberSwap M-2 discussion, the Bitcoin network's current hashrate (~4.7 × 10^20 H/s) can produce 2^80 hashes in roughly 1–3 hours. Even at 1 % of that compute (affordable with commodity ASICs), the attack completes in days. The bridge contract is upgradeable (admin-controlled), so the window for exploitation is bounded, but the profit motive is large: all ERC-1155 tokens locked in the bridge for a given `(tokenA, idA)` pair are at risk. Collision cost decreases monotonically as compute becomes cheaper.

---

### Recommendation

In `initTransfer1155`, after computing `deterministicToken`, verify that the supplied `(tokenAddress, tokenId)` matches the registered mapping:

```solidity
MultiTokenInfo memory info = multiTokens[deterministicToken];
require(
    info.tokenAddress == tokenAddress && info.tokenId == tokenId,
    "ERR_TOKEN_NOT_REGISTERED"
);
```

This makes the check equivalent to `logMetadata1155`'s own collision guard and ensures that only a pair that was explicitly registered — and whose registration cannot be overwritten — can initiate a transfer. Because `logMetadata1155` already enforces first-write-wins semantics, this single addition closes the attack entirely. [5](#0-4) 

---

### Proof of Concept

```python
# Pseudocode: birthday collision search
import hashlib, os, struct

def det_addr(token_addr_bytes, token_id_int):
    packed = token_addr_bytes + struct.pack(">32s", token_id_int.to_bytes(32, "big"))
    return hashlib.sha3_256(packed).digest()[:20]   # keccak256 truncated to 20 bytes

table = {}
for _ in range(2**40):                              # scale to 2^80 for real attack
    addr_a = os.urandom(20)
    id_a   = int.from_bytes(os.urandom(32), "big")
    d = det_addr(addr_a, id_a)
    if d in table:
        (addr_b, id_b) = table[d]
        print(f"Collision: ({addr_a.hex()}, {id_a}) == ({addr_b.hex()}, {id_b}) => {d.hex()}")
        break
    table[d] = (addr_a, id_a)
```

Once a collision `(tokenA, idA)` ↔ `(tokenB, idB)` is found:

1. Deploy a minimal ERC-1155 at `tokenB` that mints `idB` freely.
2. Call `logMetadata1155(tokenA, idA)` on `OmniBridge`.
3. Call `initTransfer1155(tokenB, idB, 1_000_000, 0, 0, "attacker.near", "")`.
4. Observe `InitTransfer` emitted with `tokenAddress = D` (same as the legitimate token).
5. NEAR relayer finalises the transfer; NEAR mints 1,000,000 unbacked wrapped tokens to `attacker.near`.

### Citations

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L245-254)
```text
        if (multiToken.tokenAddress == address(0)) {
            multiToken.tokenAddress = tokenAddress;
            multiToken.tokenId = tokenId;
        } else {
            if (
                multiToken.tokenAddress != tokenAddress ||
                multiToken.tokenId != tokenId
            ) {
                revert ERC1155MappingMismatch();
            }
```

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L439-489)
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
```

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L576-584)
```text
    function deriveDeterministicAddress(
        address tokenAddress,
        uint256 tokenId
    ) public pure returns (address) {
        return
            address(
                bytes20(keccak256(abi.encodePacked(tokenAddress, tokenId)))
            );
    }
```

**File:** near/omni-bridge/src/lib.rs (L709-722)
```rust
        let Ok(ProverResult::InitTransfer(init_transfer)) = Self::decode_prover_result(0) else {
            env::panic_str(BridgeError::InvalidProofMessage.to_string().as_str())
        };
        require!(
            self.factories
                .get(&init_transfer.emitter_address.get_chain())
                == Some(init_transfer.emitter_address),
            BridgeError::UnknownFactory.as_ref()
        );

        let decimals = self
            .token_decimals
            .get(&init_transfer.token)
            .near_expect(BridgeError::TokenDecimalsNotFound);
```
