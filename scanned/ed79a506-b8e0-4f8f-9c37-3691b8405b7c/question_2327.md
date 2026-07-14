# Q2327: update_metadata trusts attacker-shaped state across an internal boundary

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `update_metadata` and control security-critical fields that cross from one production layer to another without changing the external attacker model so that `DIDWallet.update_metadata` in `chia/wallet/did_wallet/did_wallet.py` executes a path where make `update_metadata` trust attacker-shaped state that another nearby layer should have revalidated before use, violating the invariant that every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/did_wallet/did_wallet.py:1053 `DIDWallet.update_metadata`
- Entrypoint: wallet RPC or wallet sync flow reaching `update_metadata`
- Attacker controls: security-critical fields that cross from one production layer to another without changing the external attacker model
- Exploit idea: make `update_metadata` trust attacker-shaped state that another nearby layer should have revalidated before use
- Invariant to test: every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: drive one attacker-controlled object across adjacent layers into `chia/wallet/did_wallet/did_wallet.py:update_metadata` and assert the receiving layer revalidates every security-critical field before trusting it
