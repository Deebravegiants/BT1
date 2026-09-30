# [?] core/txpool/blobpool: avoid possible zero index panic (#30430) (#579)

## Summary
Severity: Unknown
Chain: Ronin
Component: axieinfinity/ronin-archive
Published: 2024-09-20
Source: https://github.com/axieinfinity/ronin-archive/commit/75cad3de20513acb6f4bd7c2882edc195a36a2c1
Type: security-commit

## Details
core/txpool/blobpool: avoid possible zero index panic (#30430) (#579)

commit https://github.com/ethereum/go-ethereum/commit/0dd7e82c0aef3c27303b4a7b30016790dda949d4.

This situation(`len(txs) == 0`) rarely occurs, but if it does, it will
panic.

---------

Co-authored-by: maskpp <maskpp266@gmail.com>
Co-authored-by: Martin HS <martin@swende.se>

## Patch
### core/txpool/blobpool/blobpool.go
```diff
@@ -555,7 +555,7 @@ func (p *BlobPool) recheck(addr common.Address, inclusions map[common.Hash]uint6
 			ids    []uint64
 			nonces []uint64
 		)
-		for txs[0].nonce < next {
+		for len(txs) > 0 && txs[0].nonce < next {
 			ids = append(ids, txs[0].id)
 			nonces = append(nonces, txs[0].nonce)
 
```
