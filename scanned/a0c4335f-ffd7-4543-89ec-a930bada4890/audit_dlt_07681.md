# [?] Fixed a panic in span fetching (#14078)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2025-03-05
Source: https://github.com/erigontech/erigon/commit/c625d4831f2f7e0cbfb3e684f53da52a67601b49
Type: security-commit

## Details
Fixed a panic in span fetching (#14078)

## Patch
### polygon/bor/spanner.go
```diff
@@ -18,6 +18,7 @@ package bor
 
 import (
 	"encoding/hex"
+	"errors"
 	"math/big"
 
 	"github.com/erigontech/erigon-lib/log/v3"
@@ -128,6 +129,10 @@ func (c *ChainSpanner) GetCurrentProducers(spanId uint64, chain ChainHeaderReade
 
 	span := chain.BorSpan(spanId)
 
+	if span == nil {
+		return nil, errors.New("no span found")
+	}
+
 	producers := make([]*valset.Validator, len(span.SelectedProducers))
 	for i := range span.SelectedProducers {
 		producers[i] = &span.SelectedProducers[i]
```
