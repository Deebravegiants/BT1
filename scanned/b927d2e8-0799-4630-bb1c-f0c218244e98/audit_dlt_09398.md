# [?] [doc] Double Spend Proof (dsproof-beta) implementation notes etc

## Summary
Severity: Unknown
Chain: Bitcoin Cash
Component: bitcoin-cash-node/bitcoin-cash-node
Published: 2021-01-25
Source: https://github.com/bitcoin-cash-node/bitcoin-cash-node/commit/8aff361bc96481272281f4fc8a8d30806921b381
Type: security-commit

## Details
[doc] Double Spend Proof (dsproof-beta) implementation notes etc

## Patch
### doc/dsproof-implementation-notes.md
```diff
@@ -0,0 +1,99 @@
+Double Spend Proofs - BCHN Implementation Notes
+===============================================
+
+This document serves a two-fold purpose:
+
+1. To give information to users of the BCHN software about expected behavior
+   of the DSProof feature which is not fully addressed in the current draft
+   specification maintained upstream
+
+2. To provide additional notes about interpretation of the upstream
+   specification in instances where more clarity is deemed useful -
+   for anyone trying to understand or implement the upstream specification.
+
+Note about upstream DSProof specification
+-----------------------------------------
+
+A copy of the most recent upstream specification should be found at
+
+<https://gitlab.com/-/snippets/1883331>
+
+It is currently in Draft, and some review discussion can be found below it.
+
+This draft specification has been merged into the common BCH specification
+repository maintained by Software Verde, and has since started to appear
+on the downstream sites such as
+
+<https://documentation.cash/protocol/network/messages/dsproof-beta>
+
+We cannot currently include this specification in the documentation set
+here because its license is CC-BY-SA and it would need to be dual-licensed
+under MIT license to be included with the BCHN client.
+
+
+DSProof implementation behavior in BCHN
+---------------------------------------
+
+As the DSProof specification is still in Draft, we are providing here
+some additional notes on the BCHN implementation of this feature.
+
+1. The DSProof functionality is enabled by default, this means
+   DS proofs are created and relayed. Both creation and relay  can
+   be disabled by setting `doublespendproof=0` in the configuration
+   or passing `-doublespendproof=0` or `-disabledoublespendproof`
+   on the command line.
+
+2. DSProofs are issued even for double spent transactions whose
+   direct ancestors are not confirmed.
+   This includes transactions whose ancestry includes unspent
+   P2SH inputs, or unspent transactions signed with ANYONECANPAY
+   hash type.
+
+3. If a transaction that is double spent is in the mempool (or UTXO set)
+   and has descendants in the mempool, a DSProof is currently only
+   issued for the double spent transaction itself.
+   There is no notification or query mechanism yet to inform that the
+   descendants have now been put at risk too due to the double spend.
+
+4. The GUI wallet does not display any notice yet when a transaction
+   pending to be confirmed is double spent.
+
+5. There is a parameter for debug logging of DSProof functionality.
+   It can be enabled by by adding `dsproof` to the debug flags.
+
+6. Orphans:
+   - DS proofs are stored as either orphans or non-orphans
+   - Orphans are proofs we have received for which the conflicting
+     transaction (or UTXO) has not yet been seen, therefore the proof
+     cannot be validated yet when it is seen.
+   - There is a maximum number of orphans (default 65535) but in
+     practice an extra 25% is allowed for performance reasons.
+     The high water mark is 1.25 * max = 81918, if exceeded, the oldest
+     orphans are removed until the subsystem is below the high water
+     mark again.
+   - There is an orphan expiry time which defaults to 90 seconds.
+   - A periodic cleanup thread runs every 60 seconds, to reap expired
+     orphans.
+   - Orphans can become non-orphans when the necessary information to
+     validate them, is received.
+   - Non-orphan proofs are not subject to automatic expiry.
+   - Misbehaving peers that supplied orphan proofs which turn out to be fake
+     (after a valid proof is received that shows the orphan was fake)
+     will get punished (misbehaviour score increased by 10 points).
+
+
+Notes on the upstream specification(s)
+--------------------------------------
+
+1. The sizes of the `FirstSpender` and `DoubleSpender` fields are variable.
+
+2. The value of the  first `list-size` field in the spender record
+   (the `Number-of-pushdata's`) is currently fixed to 1, and thus its
+   encoding only occupies a single byte.
+
+3. The specification license (CC-BY-SA) is stricter than MIT, preventing
+   its direct inclusion together with the BCHN documentation.
+
+4. The document linked in the References can also be found within BCHN
+   upgrade documents at
+   <https://upgradespecs.bitcoincashnode.org/replay-protected-sighash/>
```

### doc/release-notes.md
```diff
@@ -16,12 +16,28 @@ Bitcoin Cash Node version 22.3.0 is now available from:
 
 ## Network changes
 
-...
+The `dsproof-beta` network message can be emitted and relayed
+when Double Spend Proofs are enabled (which they are by default).
 
 
 ## Added functionality
 
-...
+### Double Spend Proofs (DSProof)
+
+This release adds Double Spend Proofs that are compatible
+with the published `dsproof-beta` message specification and
+existing implementations in Bitcoin Unlimited and Flowee The Hub.
+
+Double spend proofs are enabled by default, but can be turned
+off with the `doublespendproof=0` configuration setting.
+
+This functionality is still in beta. In future BCHN releases
+we plan to gradually add more application interfaces to query
+double spend proof information about transactions and to provide
+wallet user with double spend notifications.
+
+Please refer to </doc/dsproof-implementation-notes.md> for more
+information details on the DSProof implementation in BCHN.
 
 
 ## Deprecated functionality
@@ -163,7 +179,7 @@ all of them on our GitLab repository.
 
 #### Interfaces / RPC
 
-...
+- TODO: double spend proof network message commits
 
 #### Peformance optimizations
 
```

### mkdocs.yml
```diff
@@ -318,6 +318,7 @@ nav:
         - Bitcoin Cash upgrades: doc/bch-upgrades.md
         - getblocktemplatelight: doc/getblocktemplatelight.md
         - XVersionMessage: doc/xversionmessage.md
+        - DSProof implementation notes: doc/dsproof-implementation-notes.md
     - Development:
         - Contributing: CONTRIBUTING.md
         - GitLab rules & guidelines: doc/bchn-gitlab-usage-rules-and-guidelines.md
```
