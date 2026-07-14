# Q3462: new_peak_from_untrusted trusts attacker-shaped state across an internal boundary

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `new_peak_from_untrusted` and control security-critical fields that cross from one production layer to another without changing the external attacker model so that `WalletNode.new_peak_from_untrusted` in `chia/wallet/wallet_node.py` executes a path where make `new_peak_from_untrusted` trust attacker-shaped state that another nearby layer should have revalidated before use, violating the invariant that every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/wallet_node.py:1273 `WalletNode.new_peak_from_untrusted`
- Entrypoint: wallet RPC or wallet sync flow reaching `new_peak_from_untrusted`
- Attacker controls: security-critical fields that cross from one production layer to another without changing the external attacker model
- Exploit idea: make `new_peak_from_untrusted` trust attacker-shaped state that another nearby layer should have revalidated before use
- Invariant to test: every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: drive one attacker-controlled object across adjacent layers into `chia/wallet/wallet_node.py:new_peak_from_untrusted` and assert the receiving layer revalidates every security-critical field before trusting it
