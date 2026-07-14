# Q128: delete_key_by_fingerprint trusts attacker-shaped state across an internal boundary

## Question
Can an unprivileged attacker reach keychain command path reaching `delete_key_by_fingerprint` and control security-critical fields that cross from one production layer to another without changing the external attacker model so that `KeychainServer.delete_key_by_fingerprint` in `chia/daemon/keychain_server.py` executes a path where make `delete_key_by_fingerprint` trust attacker-shaped state that another nearby layer should have revalidated before use, violating the invariant that every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/daemon/keychain_server.py:272 `KeychainServer.delete_key_by_fingerprint`
- Entrypoint: keychain command path reaching `delete_key_by_fingerprint`
- Attacker controls: security-critical fields that cross from one production layer to another without changing the external attacker model
- Exploit idea: make `delete_key_by_fingerprint` trust attacker-shaped state that another nearby layer should have revalidated before use
- Invariant to test: every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: drive one attacker-controlled object across adjacent layers into `chia/daemon/keychain_server.py:delete_key_by_fingerprint` and assert the receiving layer revalidates every security-critical field before trusting it
