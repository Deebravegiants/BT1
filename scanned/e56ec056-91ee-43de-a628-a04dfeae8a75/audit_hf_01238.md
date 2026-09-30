# [C] Incorrect error type when initiating message not found leads to state transition failing, unprovable new state

## Summary
Severity: Critical
Contest weight: 0.4199
Dataset id: 5737
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When the log index in an execute message log is too big (more than number of logs in the block), the Contains check returns an error that isn't correctly handled. The error message is untyped and the check in isInvalidMessageError will return false for them. That means the error will not trigger the replacement of the block with a "deposits only" version (expected behavior).  
Instead, the state transition fails. This allows a single invalid execute message log in a single block to prevent the super chain state transition from executing -- and thus make the new state unprovable.

## Proof of Concept
This test case can be added to interop_test.go:  
```go
{
    name: "ReplaceChainB-LogIndexTooBig",
    testCase: consolidationTestCase{
        logBuilderFn: func(includeBlockNumbers map[supervisortypes.ChainIndex]uint64, config *staticConfigSource) map[supervisortypes.ChainIndex][]*gethTypes.Log {
            init1 := &gethTypes.Log{
                Address: initiatingMessageOrigin,
                Topics: []common.Hash{initiatingMessageTopic},
            }
            init2 := &gethTypes.Log{
                Address: initiatingMessageOrigin2,
                Topics: []common.Hash{initiatingMessageTopic},
            }
            exec := createExecMessage(includeBlockNumbers[chainA], config, chainA)
            exec.Identifier.Origin = init2.Address
            exec.Identifier.LogIndex = 1_000_000
            return map[supervisortypes.ChainIndex][]*gethTypes.Log{
                chainA: {init1, init2},
                chainB: {convertExecutingMessageToLog(t, exec)},
            }
        },
        expectBlockReplacements: func(config *staticConfigSource) []supervisortypes.ChainIndex {
            return []supervisortypes.ChainIndex{chainB}
        },
    },
}
```

## Recommendation
The error returned should be of a type that can trigger a block replacement. For example:  
```go
return supervisortypes.BlockSeal{}, fmt.Errorf("log not found: %w", supervisortypes.ErrConflict)
```
