### Title
`AGG_SIG_UNSAFE` in DID Recovery Attestment Signs Only `newpuz` Without Binding to the Recovering DID, Enabling Cross-DID Signature Replay - (File: chia/wallet/did_wallet/did_wallet_puzzles.py)

### Summary
The `create_recovery_message_puzzle` function emits an `AGG_SIG_UNSAFE` condition that signs only the new puzzle hash (`newpuz`). Because the recovering DID's coin ID is committed only via a `CREATE_COIN_ANNOUNCEMENT` — not included in the signed message — a valid attestment signature for DID_A's recovery can be replayed verbatim to authorize DID_B's recovery to the same `newpuz`, without the backup-DID holder's consent for DID_B.

### Finding Description

`create_recovery_message_puzzle` constructs the on-chain attestment puzzle used in DID social recovery:

```python
puzzle = Program.to(
    (
        1,
        [
            [ConditionOpcode.CREATE_COIN_ANNOUNCEMENT, recovering_coin_id],
            [ConditionOpcode.AGG_SIG_UNSAFE, bytes(pubkey), newpuz],
        ],
    )
)
``` [1](#0-0) 

The `AGG_SIG_UNSAFE` condition requires a BLS signature over the raw bytes of `newpuz` with no additional data appended — no coin ID, no network-specific domain tag (`AGG_SIG_ME_ADDITIONAL_DATA`), and crucially no `recovering_coin_id`. [2](#0-1) 

`AGG_SIG_UNSAFE` is the only AGG_SIG variant that appends nothing to the message before verification; all other variants (`AGG_SIG_ME`, `AGG_SIG_PARENT`, etc.) append coin-specific or network-specific data. [3](#0-2) 

The `recovering_coin_id` is bound only through the `CREATE_COIN_ANNOUNCEMENT` output of the attestment coin. The DID recovery spend asserts that announcement, so the recovering DID is identified — but the *signature* itself is blind to it. Any attestment coin that embeds the same `(pubkey, newpuz)` pair will accept the same BLS signature, regardless of which `recovering_coin_id` it announces.

`create_spend_for_message` materialises this into a spendable coin: [4](#0-3) 

### Impact Explanation

An attacker who observes a broadcast attestment spend for DID_A's recovery to `newpuz` (signed by backup-DID holder Alice) can:

1. Construct a new zero-value coin whose puzzle is `create_recovery_message_puzzle(DID_B_coin_id, newpuz, Alice_pubkey)`.
2. Spend that coin using Alice's already-published signature — the `AGG_SIG_UNSAFE` condition is satisfied because the signed bytes (`newpuz`) are identical.
3. The new attestment coin emits `CREATE_COIN_ANNOUNCEMENT(DID_B_coin_id)`.
4. A DID recovery spend for DID_B asserts that announcement, completing an unauthorized recovery of DID_B to `newpuz`.

This constitutes unauthorized singleton mutation of a DID — the owner of `newpuz` gains control of DID_B without Alice ever consenting to attest for DID_B's recovery. This falls under **High: bypass of wallet authorization enabling unauthorized singleton mutation**.

### Likelihood Explanation

Preconditions: (a) at least one DID with a non-empty recovery list (the feature is deprecated but the code remains fully callable in production); (b) a backup-DID holder has published an attestment for any DID recovery to a known `newpuz`; (c) a second DID shares the same backup-DID holder. All three conditions are observable on-chain by any unprivileged party. No key material or privileged access is required beyond reading the blockchain.

### Recommendation

Replace `AGG_SIG_UNSAFE` with a condition that binds the signature to the specific recovery context. The minimal fix is to include `recovering_coin_id` in the signed message:

```python
[ConditionOpcode.AGG_SIG_UNSAFE, bytes(pubkey), recovering_coin_id + newpuz]
```

A stronger fix is to use `AGG_SIG_ME` on the attestment coin itself, which automatically appends the coin's own ID and the network's `AGG_SIG_ME_ADDITIONAL_DATA`, providing both per-recovery and per-network binding. This mirrors the domain-separation properties that all other Chia spend conditions already provide. [5](#0-4) 

### Proof of Concept

```
Setup:
  Alice_DID is listed as backup for both Bob_DID and Charlie_DID.
  Bob initiates recovery: recovering_coin_id = Bob_DID_coin, newpuz = P.
  Alice creates attestment A1 = create_recovery_message_puzzle(Bob_DID_coin, P, Alice_pk).
  Alice signs: sig = AugSchemeMPL.sign(Alice_sk, P)   # AGG_SIG_UNSAFE over P only
  A1 is broadcast on-chain; sig is visible in the spend bundle.

Attack:
  Attacker constructs A2 = create_recovery_message_puzzle(Charlie_DID_coin, P, Alice_pk).
  A2 has puzzle hash ≠ A1 (different recovering_coin_id) but the same AGG_SIG_UNSAFE(Alice_pk, P).
  Attacker spends A2 with sig — valid, because AugSchemeMPL.verify(Alice_pk, P, sig) == True.
  A2 emits CREATE_COIN_ANNOUNCEMENT(Charlie_DID_coin).
  Attacker submits DID recovery spend for Charlie_DID asserting A2's announcement.
  Charlie_DID is recovered to P (controlled by Bob/attacker) without Alice's consent for Charlie.
``` [6](#0-5) [7](#0-6)

### Citations

**File:** chia/wallet/did_wallet/did_wallet_puzzles.py (L137-171)
```python
def create_recovery_message_puzzle(recovering_coin_id: bytes32, newpuz: bytes32, pubkey: G1Element) -> Program:
    """
    Create attestment message puzzle
    :param recovering_coin_id: ID of the DID coin needs to recover
    :param newpuz: New wallet puzzle hash
    :param pubkey: New wallet pubkey
    :return: Message puzzle
    """
    puzzle = Program.to(
        (
            1,
            [
                [ConditionOpcode.CREATE_COIN_ANNOUNCEMENT, recovering_coin_id],
                [ConditionOpcode.AGG_SIG_UNSAFE, bytes(pubkey), newpuz],
            ],
        )
    )
    return puzzle


def create_spend_for_message(
    parent_of_message: bytes32, recovering_coin: bytes32, newpuz: bytes32, pubkey: G1Element
) -> CoinSpend:
    """
    Create a CoinSpend for a atestment
    :param parent_of_message: Parent coin ID
    :param recovering_coin: ID of the DID coin needs to recover
    :param newpuz: New wallet puzzle hash
    :param pubkey: New wallet pubkey
    :return: CoinSpend
    """
    puzzle = create_recovery_message_puzzle(recovering_coin, newpuz, pubkey)
    coin = Coin(parent_of_message, puzzle.get_tree_hash(), uint64(0))
    solution = Program.to([])
    return make_spend(coin, puzzle, solution)
```

**File:** chia/consensus/condition_tools.py (L147-152)
```python
    for cwa in conditions_dict.get(ConditionOpcode.AGG_SIG_UNSAFE, []):
        validate_cwa(cwa)
        for disallowed in data.values():
            if cwa.vars[1].endswith(disallowed):
                raise ConsensusError(Err.INVALID_CONDITION)
        ret.append((G1Element.from_bytes(cwa.vars[0]), cwa.vars[1]))
```

**File:** chia/consensus/condition_tools.py (L154-165)
```python
    for opcode in [
        ConditionOpcode.AGG_SIG_PARENT,
        ConditionOpcode.AGG_SIG_PUZZLE,
        ConditionOpcode.AGG_SIG_AMOUNT,
        ConditionOpcode.AGG_SIG_PUZZLE_AMOUNT,
        ConditionOpcode.AGG_SIG_PARENT_AMOUNT,
        ConditionOpcode.AGG_SIG_PARENT_PUZZLE,
        ConditionOpcode.AGG_SIG_ME,
    ]:
        for cwa in conditions_dict.get(opcode, []):
            validate_cwa(cwa)
            ret.append((G1Element.from_bytes(cwa.vars[0]), make_aggsig_final_message(opcode, cwa.vars[1], coin, data)))
```

**File:** chia/types/condition_opcodes.py (L18-19)
```python
    AGG_SIG_UNSAFE = bytes([49])
    AGG_SIG_ME = bytes([50])
```
