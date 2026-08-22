# [?] triedb/pathdb: fix 32-bit integer overflow in history trienode decoder (#33098)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2025-11-07
Source: https://github.com/ethereum/go-ethereum/commit/d2a5dba48f31031e8f9b1b4942a1e29e54d97079
Type: security-commit

## Details
triedb/pathdb: fix 32-bit integer overflow in history trienode decoder (#33098)

failed in 32bit:

```
--- FAIL: TestDecodeSingleCorruptedData (0.00s)
panic: runtime error: slice bounds out of range [:-1501805520] [recovered, repanicked]

goroutine 38872 [running]:
testing.tRunner.func1.2({0x838db20, 0xa355620})
	/opt/actions-runner/_work/_tool/go/1.25.3/x64/src/testing/testing.go:1872 +0x29b
testing.tRunner.func1()
	/opt/actions-runner/_work/_tool/go/1.25.3/x64/src/testing/testing.go:1875 +0x414
panic({0x838db20, 0xa355620})
	/opt/actions-runner/_work/_tool/go/1.25.3/x64/src/runtime/panic.go:783 +0x103
github.com/ethereum/go-ethereum/triedb/pathdb.decodeSingle({0x9e57500, 0x1432, 0x1432}, 0x0)
	/opt/actions-runner/_work/go-ethereum/go-ethereum/triedb/pathdb/history_trienode.go:399 +0x18d6
github.com/ethereum/go-ethereum/triedb/pathdb.TestDecodeSingleCorruptedData(0xa2db9e8)
	/opt/actions-runner/_work/go-ethereum/go-ethereum/triedb/pathdb/history_trienode_test.go:698 +0x180
testing.tRunner(0xa2db9e8, 0x83c86e8)
	/opt/actions-runner/_work/_tool/go/1.25.3/x64/src/testing/testing.go:1934 +0x114
created by testing.(*T).Run in goroutine 1
	/opt/actions-runner/_work/_tool/go/1.25.3/x64/src/testing/testing.go:1997 +0x4b4
FAIL	github.com/ethereum/go-ethereum/triedb/pathdb	41.453s
?   	github.com/ethereum/go-ethereum/version	[no test files]
FAIL
```

Found in
https://github.com/ethereum/go-ethereum/actions/runs/18912701345/job/53990136071?pr=33052
