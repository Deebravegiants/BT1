# [H] Some btc incoming transfers can fail due to invalid evm address parsing

## Summary
Severity: High
Contest weight: 0.5571
Dataset id: 1861
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The bridge uses polling of rune utxos to ms address (2500 at a time) to determine which transfers must be executed on other chains (solana or bitlayer evm). When parsing an evm address from the runestone field ”43”, if the data is too short (e.g only one uint128), an unhandled panic will be triggered (runtimeerror:sliceboundsoutofrange[:20]withcapacity16). This will not halt the bridge program because errors of the go routine are still recovered, but the bridge will attempt to scan the transfer and fail repeatedly until it can be skipped because more than 2500 utxos are available. In that case some other transfers may be skipped alongside the invalid one with high probability.
In chain_btc.go#L37-L53:
```go
if ta, ok := tx.GetJ("fields")["43"]; ok {
    bs := []byte{}
    for i, n := range ta.([]interface{}) {
        bss := StringToBi(n.(string)).Bytes()
        slices.Reverse(bss)
        bs = append(bs, bss...)
        for len(bs) < (i+1)*16 {
            bs = append(bs, 0) // when number starts with 0 we will be missing bytes
        }
    }
    if targetNetwork == NetworkSolana {
        targetAddress = BytesToBase58(bs)
    } else if targetNetwork == NetworkBitlayer {
        // TODO generalize condition for all evm targets
        targetAddress = hexutil.Encode(bs[:20])
    }
}
```
Internal pre-conditions
External pre-conditions
Attack Path
1. A malicious actor sends some very small amount of any rune (even some rune without value which is not whitelisted by the system because this is not checked during the scan), and adds the message field ”43” with only 1 uint128.
1/ Processing of incoming transfers on btc chain is blocked until the window of the indexer query is reached (2500) 2/ The bridge scanner will skip some utxos with high probability during high usage periods (due to the fact that the processing halted until reaching the limit of 2500 utxos). Indeed, unless the limit of 2500 is crossed by exactly 1 utxo, some utxos will be skipped (because only latest 2500 are processed)

## Proof of Concept
Add the following test to bridge_test.go:
```go
func TestInvalidEvmAddressDecode(t *testing.T) {
    ta := [1]string{}
    ta[0] = "43962546600517487046958341907937552909"
    bs := []byte{}
    for i, n := range ta {
        bss := StringToBi(n).Bytes()
        slices.Reverse(bss)
        bs = append(bs, bss...)
        for len(bs) < (i+1)*16 {
            bs = append(bs, 0) // when number starts with 0 we will be missing bytes
        }
    }
    // TODO generalize condition for all evm targets
    hexutil.Encode(bs[:20])
}
go test ./bridge -run "TestInvalidEvmAddressDecode" -test.v
=== RUN TestEvmAddressDecode
--- FAIL: TestEvmAddressDecode (0.00s)
panic: runtime error: slice bounds out of range [:20] with capacity 16 [recovered]
panic: runtime error: slice bounds out of range [:20] with capacity 16
goroutine 20 [running]:
testing.tRunner.func1.2({0xb618e0, 0xc0001486d8})
/usr/lib/go/src/testing/testing.go:1632 +0x230
testing.tRunner.func1()
/usr/lib/go/src/testing/testing.go:1635 +0x35e
panic({0xb618e0?, 0xc0001486d8?})
/usr/lib/go/src/runtime/panic.go:785 +0x132
runemine-bridge/bridge.TestEvmAddressDecode(0xc000167380?)
+0x20b
testing.tRunner(0xc000167380, 0xcb8be0)
/usr/lib/go/src/testing/testing.go:1690 +0xf4
created by testing.(*T).Run in goroutine 1
/usr/lib/go/src/testing/testing.go:1743 +0x390
FAIL runemine-bridge/bridge 0.015s
FAIL
```

## Recommendation
In the case the target is EVM, please consider padding the bytes array bs to be at least 20 bytes long.
