This confirms the analog: `CBORParseTask` (task type `cborparse`) is used in Direct Request/`runlog` job pipelines to decode the `cborPayload` field of an `OracleRequest` on-chain event — a value that comes directly from `data` submitted in an arbitrary Ethereum transaction by any unprivileged caller of the requesting contract (see the `CBORDietEmpty`/`CBORStdString` DAG templates and `DirectRequestJobSpec`/`DirectRequestTxPipelineSpec` in `deployment/environment/nodeclient/chainlink_models.go:793-812`, which wire `decode_log.cborPayload` straight into `cborparse`). `CoerceInterfaceMapToStringMap` in `core/cbor/cbor.go` recurses without any depth bound over the resulting `map[any]any`/`[]any` tree, exactly like the vulnerable `_.flatten`/`_.isEqual` pattern in the advisory. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

### Title
Unbounded recursion in `CoerceInterfaceMapToStringMap` allows unprivileged on-chain requester to crash a Chainlink node via deeply nested CBOR payload - ([File: core/cbor/cbor.go])

### Summary
`cbor.CoerceInterfaceMapToStringMap` (`core/cbor/cbor.go:77-117`) recursively walks a decoded CBOR value (`map[any]any` / `map[string]any` / `[]any`) with no depth limit, calling itself once per nesting level. It is invoked from `cbor.ParseDietCBOR` (`core/cbor/cbor.go:16-35`), which is used by the `cborparse` pipeline task (`core/services/pipeline/task.cborparse.go:52-61`) in "diet" mode. This task is the standard way Direct Request ("runlog") jobs decode the `cborPayload` field of the on-chain `OracleRequest(...)` event, as shown by the `decode_log -> decode_cbor` templates in `core/services/pipeline/runner_test.go:365-390` and the job templates in `deployment/environment/nodeclient/chainlink_models.go:793-812`.

### Finding Description
`OracleRequest` events are emitted whenever any external, unauthenticated Ethereum account calls the requesting contract's `oracleRequest`/similar function and supplies an arbitrary `bytes cborPayload` argument — there is no on-chain validation of CBOR structure or nesting depth. The node's pipeline decodes this event log via `ethabidecodelog`, then feeds the raw `cborPayload` bytes into the `cborparse` task, which calls `cbor.ParseDietCBOR` → `cbor.UnmarshalFirst` → `CoerceInterfaceMapToStringMap`. Because `CoerceInterfaceMapToStringMap` recurses into every nested `map[any]any`, `map[string]any`, and `[]any` element with no depth cap, a CBOR payload consisting of thousands of nested single-element maps/arrays will drive the Go call stack to exhaustion, causing the process to crash with a fatal `runtime: goroutine stack exceeds ... - fatal error: stack overflow`. This is a Go stack overflow, which (unlike a Go `panic`) cannot be recovered by any `defer/recover`, so it takes down the entire node process, not just the one job run.

This is directly analogous to the underscore.js `_.flatten`/`_.isEqual` bug class: both are recursive tree-walking functions applied to attacker-controlled nested data with no depth bound.

### Impact Explanation
Any address on the corresponding chain can call the requester contract to emit an `OracleRequest` with a maliciously deep CBOR payload, with no special permissions, keys, or allowlist membership required. Because a Go stack overflow crashes the entire node binary (fatal, unrecoverable), this is a full denial-of-service against the Chainlink node process — it would drop all pending and running jobs, not just the one processing the malicious request, and requires operator intervention to restart the node.

### Likelihood Explanation
Likelihood is high for nodes running Direct Request (`directrequest`)/runlog jobs, which is a widely used job type: the on-chain surface (any account emitting `OracleRequest` with a `cborPayload` bytes field) is fully unauthenticated and permissionless, and the crafted payload (a chain of a few thousand nested single-element CBOR maps or arrays) is trivial and inexpensive to construct as calldata.

### Recommendation
Add a maximum recursion/nesting depth to `CoerceInterfaceMapToStringMap` (and reject/return an error once exceeded), and/or configure the underlying `fxamacker/cbor` decoder with `cbor.DecOptions{MaxNestedLevels: N}` (a supported option) before calling `UnmarshalFirst` in `ParseDietCBOR`/`ParseStandardCBOR`. A depth limit of a few hundred levels is more than sufficient for legitimate use cases while preventing stack exhaustion.

### Proof of Concept
```go
// Construct CBOR bytes representing ~100,000 levels of nested single-element
// maps, e.g. {"a": {"a": {"a": ... "leaf" ... }}}, using the cbor library
// (or equivalent raw byte construction using indefinite-length map markers
// 0xbf ... 0xff nested repeatedly), matching the "diet" CBOR format expected
// by ParseDietCBOR (see autoAddMapDelimiters in core/cbor/cbor.go).
//
// Then:
b := buildDeeplyNestedDietCBOR(100000)
_, err := cbor.ParseDietCBOR(b) // crashes the process with a stack overflow
                                 // before returning any error
```
On-chain, this same payload would be submitted as the `_data`/`cborPayload` argument to the requester contract's request function by any unprivileged EOA, and the node would crash while processing the resulting `OracleRequest` log through the `cborparse` pipeline task.

### Citations

**File:** core/cbor/cbor.go (L77-117)
```go
func CoerceInterfaceMapToStringMap(in any) (any, error) {
	switch typed := in.(type) {
	case map[string]any:
		for k, v := range typed {
			coerced, err := CoerceInterfaceMapToStringMap(v)
			if err != nil {
				return nil, err
			}
			typed[k] = coerced
		}
		return typed, nil
	case map[any]any:
		m := map[string]any{}
		for k, v := range typed {
			coercedKey, ok := k.(string)
			if !ok {
				return nil, fmt.Errorf("unable to coerce key %T %v to a string", k, k)
			}
			coerced, err := CoerceInterfaceMapToStringMap(v)
			if err != nil {
				return nil, err
			}
			m[coercedKey] = coerced
		}
		return m, nil
	case []any:
		r := make([]any, len(typed))
		for i, v := range typed {
			coerced, err := CoerceInterfaceMapToStringMap(v)
			if err != nil {
				return nil, err
			}
			r[i] = coerced
		}
		return r, nil
	case big.Int:
		value, _ := (in).(big.Int)
		return &value, nil
	default:
		return in, nil
	}
```

**File:** core/services/pipeline/task.cborparse.go (L52-61)
```go
	switch mode {
	case "diet":
		// NOTE: In diet mode, cbor_parse ASSUMES that the incoming CBOR is a
		// map. In the case that data is entirely missing, we assume it was the
		// empty map
		parsed, err := cbor.ParseDietCBOR(data)
		if err != nil {
			return Result{Error: errors.Wrapf(ErrBadInput, "CBORParse: data: %v", err)}, runInfo
		}
		return Result{Value: parsed}, runInfo
```

**File:** core/services/pipeline/runner_test.go (L365-390)
```go
const (
	CBORDietEmpty = `
decode_log  [type="ethabidecodelog"
             data="$(jobRun.logData)"
             topics="$(jobRun.logTopics)"
             abi="OracleRequest(address requester, bytes32 requestId, uint256 payment, address callbackAddr, bytes4 callbackFunctionId, uint256 cancelExpiration, uint256 dataVersion, bytes cborPayload)"]

decode_cbor [type="cborparse"
             data="$(decode_log.cborPayload)"
			 mode=diet]

decode_log -> decode_cbor;
`
	CBORStdString = `
decode_log  [type="ethabidecodelog"
             data="$(jobRun.logData)"
             topics="$(jobRun.logTopics)"
             abi="OracleRequest(address requester, bytes32 requestId, uint256 payment, address callbackAddr, bytes4 callbackFunctionId, uint256 cancelExpiration, uint256 dataVersion, bytes cborPayload)"]

decode_cbor [type="cborparse"
             data="$(decode_log.cborPayload)"
			 mode=standard]

decode_log -> decode_cbor;
`
)
```

**File:** deployment/environment/nodeclient/chainlink_models.go (L793-812)
```go
// String representation of the pipeline
func (d *DirectRequestTxPipelineSpec) String() (string, error) {
	sourceString := `
            decode_log   [type=ethabidecodelog
                         abi="OracleRequest(bytes32 indexed specId, address requester, bytes32 requestId, uint256 payment, address callbackAddr, bytes4 callbackFunctionId, uint256 cancelExpiration, uint256 dataVersion, bytes data)"
                         data="$(jobRun.logData)"
                         topics="$(jobRun.logTopics)"]
			encode_tx  [type=ethabiencode
                        abi="fulfill(bytes32 _requestId, uint256 _data)"
                        data=<{
                          "_requestId": $(decode_log.requestId),
                          "_data": $(parse)
                         }>
                       ]
			fetch  [type=bridge name="{{.BridgeTypeAttributes.Name}}" requestData="{{.BridgeTypeAttributes.RequestData}}"];
			parse  [type=jsonparse path="{{.DataPath}}"]
            submit [type=ethtx to="$(decode_log.requester)" data="$(encode_tx)" failOnRevert=true]
			decode_log -> fetch -> parse -> encode_tx -> submit`
	return MarshallTemplate(d, "Direct request pipeline template", sourceString)
}
```
