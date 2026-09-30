# [?] go: Ignore CVE-2022-44797 until tendermint release uses newer btcd

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2022-11-08
Source: https://github.com/oasisprotocol/oasis-core/commit/53e8a0c39a95f87433b36345066de99a1366b7ee
Type: security-commit

## Details
go: Ignore CVE-2022-44797 until tendermint release uses newer btcd

## Patch
### .changelog/5024.internal.md
```diff
@@ -0,0 +1 @@
+go: Ignore CVE-2022-44797 until tendermint uses newer btcd
```

### go/.nancy-ignore
```diff
@@ -1 +1,2 @@
 CVE-2022-30591 # quic-go resource exhaustion through 0.27.0, 0.27.1 imported, false positive?
+CVE-2022-44797 # remove once tendermint uses btcd above or 0.23.2
```
