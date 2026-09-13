# [?] sync: fix KZG batch verifier deadlock on timeout (#16141)

## Summary
Severity: Unknown
Chain: Ethereum
Component: prysmaticlabs/prysm
Published: 2025-12-12
Source: https://github.com/OffchainLabs/prysm/commit/096cba5b2d597d9ce8d3160b4351177de29b2d63
Type: security-commit

## Details
sync: fix KZG batch verifier deadlock on timeout (#16141)

`validateWithKzgBatchVerifier` could timeout (12s) and once it times out
because `resChan` is unbuffered, the verifier will stuck at following
line at `verifyKzgBatch` as its waiting for someone to grab the result
from `resChan`:
```
	for _, verifier := range kzgBatch {
		verifier.resChan <- verificationErr
	}
```
Fix is to make kzg batch verification non blocking on timeouts by
buffering each request’s buffered size 1
