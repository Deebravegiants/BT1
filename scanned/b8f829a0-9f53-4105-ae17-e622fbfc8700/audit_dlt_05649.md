# [?] Fixes: GHSA-pr92-c4mc-x48r Remove System.out and System.err logging from P256VerifyPrecompile (#11092)

## Summary
Severity: Unknown
Chain: Ethereum
Component: hyperledger/besu
Published: 2026-08-20
Source: https://github.com/besu-eth/besu/commit/fbfb5f9ecdecadb88eb9acd6407e33006afaac87
Type: security-commit

## Details
Fixes: GHSA-pr92-c4mc-x48r Remove System.out and System.err logging from P256VerifyPrecompile (#11092)

* Fixes: GHSA-pr92-c4mc-x48r Remove System.out and System.err logging from P256VerifyPrecompile

Signed-off-by: Sally MacFarlane <macfarla.github@gmail.com>

---------

Signed-off-by: Sally MacFarlane <macfarla.github@gmail.com>

## Patch
### CHANGELOG.md
```diff
@@ -67,6 +67,7 @@
 - Removed the legacy `PANTHEON_` environment variable prefix for configuration options, everyone should already use the `BESU_` prefix at this time.
 
 ### Bug fixes
+- Remove `System.out`/`System.err` logging from `P256VerifyPrecompiledContract` and `BlockchainQueries` — these could leak sensitive data to stdout/stderr in production.
 - EIP-1459 DNS discovery now rejoins TXT records split across multiple `<character-string>`s. Records longer than 255 bytes were truncated, so Besu silently discarded most of every tree, resolving 832 of 3000 nodes from the mainnet tree. [#10985](https://github.com/besu-eth/besu/pull/10985)
 - Queue backward-sync targets received before peer readiness and retry when a peer connects. [#10843](https://github.com/besu-eth/besu/pull/10843)
 - Return `BLOCK_NOT_FOUND` for unknown block hashes and `GENESIS_BLOCK_NOT_TRACEABLE` for genesis blocks from `debug_traceBlockByHash`. [#10701](https://github.com/besu-eth/besu/pull/10701)
```

### ethereum/api/src/main/java/org/hyperledger/besu/ethereum/api/query/BlockchainQueries.java
```diff
@@ -978,7 +978,6 @@ private List<LogWithMetadata> matchingLogsCached(
         }
       }
     } catch (final IOException e) {
-      e.printStackTrace(System.out);
       LOG.error("Error reading cached log blooms", e);
     }
     return results;
```

### evm/src/main/java/org/hyperledger/besu/evm/precompile/P256VerifyPrecompiledContract.java
```diff
@@ -168,7 +168,6 @@ public PrecompileContractResult computePrecompile(
 
     } catch (Exception e) {
       LOG.warn("P256VERIFY verification failed: {}", e.getMessage());
-      System.err.println("P256VERIFY verification failed: " + e.getMessage());
       return PrecompileContractResult.success(INVALID);
     }
   }
```
