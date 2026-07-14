# Q3013: sign_message trusts attacker-shaped state across an internal boundary

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `sign_message` and control security-critical fields that cross from one production layer to another without changing the external attacker model so that `sign_message` in `chia/wallet/util/signing.py` executes a path where make `sign_message` trust attacker-shaped state that another nearby layer should have revalidated before use, violating the invariant that every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/util/signing.py:72 `sign_message`
- Entrypoint: wallet RPC or wallet sync flow reaching `sign_message`
- Attacker controls: security-critical fields that cross from one production layer to another without changing the external attacker model
- Exploit idea: make `sign_message` trust attacker-shaped state that another nearby layer should have revalidated before use
- Invariant to test: every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: drive one attacker-controlled object across adjacent layers into `chia/wallet/util/signing.py:sign_message` and assert the receiving layer revalidates every security-critical field before trusting it
