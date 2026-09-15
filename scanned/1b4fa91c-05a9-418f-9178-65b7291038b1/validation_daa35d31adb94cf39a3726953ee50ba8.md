### Title
Fragile hardcoded-offset stripping of the vault gateway request-ID owner prefix causes cross-user response ID confusion - (File: core/services/gateway/handlers/vault/handler.go)

### Summary
The vault gateway `handler` strips the `owner::requestID` prefix from response/error IDs before returning them to the user by using `strings.Index` plus a **hardcoded offset of `2`** (`resp.ID[index+2:]`), assuming the separator `vaulttypes.RequestIDSeparator` is always exactly 2 characters wide, instead of using the length of the separator constant or the safer `strings.Cut`-based helper that already exists elsewhere in the same package family.

### Finding Description
`vaulttypes.RequestIDSeparator` is defined as the string `"::"` [1](#0-0) .

The gateway-side handler prefixes the authorized owner onto the user-supplied request ID (`owner::id`) before fanning the request out to the vault DON nodes, in `authorizeAndStamp` [2](#0-1) . When building the response to hand back to the end user, JSON-RPC requires the response ID to match the original request ID, so the handler strips the owner prefix back off. It does this in two separate places using a hardcoded literal `2` as the offset to skip past the separator:

```go
index := strings.Index(resp.ID, vaulttypes.RequestIDSeparator)
if index != -1 {
    resp.ID = resp.ID[index+2:]
}
``` [3](#0-2) 

and the identical pattern for error responses:

```go
index := strings.Index(req.ID, vaulttypes.RequestIDSeparator)
if index != -1 {
    req.ID = req.ID[index+2:]
}
``` [4](#0-3) 

This is exactly the bug class described in the report: an unclear, undocumented, hardcoded magic number (`2`) standing in for `len(vaulttypes.RequestIDSeparator)`, with no test coverage tying the offset back to the separator constant, and no compile-time or run-time assertion that `RequestIDSeparator` is 2 bytes long. Elsewhere in the same codebase, the equivalent operation is implemented correctly and robustly using `strings.Cut(requestID, vaulttypes.RequestIDSeparator)` in `stripPrefixedVaultRequestID` [5](#0-4) , confirming the hardcoded-offset version in the handler is the fragile outlier, not an intentional design choice.

Additionally, `strings.Index` finds the **first** occurrence of `"::"` in the ID. Since the "owner" portion of the prefix is attacker/client-influenced content in some flows (e.g., a JWT-derived or user-controlled owner string could itself contain `::`, or a user-supplied `requestID` sent by the client could itself contain `::`), the first-match assumption combined with the hardcoded `+2` skip makes the stripping logic doubly fragile to any future change in the separator's length or content shape.

### Impact Explanation
If `RequestIDSeparator` is ever changed (e.g., to a 1-, 3-, or multi-character delimiter) without updating both hardcoded `+2` call sites, or if an owner/requestID value causes the separator to appear at an unexpected position, the resulting stripped `resp.ID`/`req.ID` returned to the client will be silently wrong (truncated by the wrong number of characters) rather than erroring out — exactly the "failing silently" and "output collisions" failure mode called out in the report. Because the gateway matches user callbacks to responses by the (stripped) request ID, an incorrectly stripped ID can produce a JSON-RPC response ID that no longer matches what the client originally sent, and in registration/callback matching pathways this creates a risk of cross-user response confusion (a response being misrouted/misattributed to the wrong pending caller) rather than a clean protocol error.

### Likelihood Explanation
Under the current constant value (`"::"`, 2 characters), the code functions correctly today, so this is a latent/fragile-code issue rather than an immediately exploitable one under the present configuration. The likelihood of triggering incorrect behavior increases significantly if: (a) the separator constant is changed by a future contributor without updating the two hardcoded offsets, or (b) any owner-derived string that is attacker-influenced (e.g., certain JWT-derived owner IDs) can embed the literal separator substring, causing `strings.Index` to match an unintended earlier position. There is no unit test asserting the offset stays in sync with `len(vaulttypes.RequestIDSeparator)`.

### Recommendation
Replace both hardcoded `index+2` offsets in `core/services/gateway/handlers/vault/handler.go` with logic derived from the separator itself, mirroring the existing robust helper:
- Use `strings.Cut(resp.ID, vaulttypes.RequestIDSeparator)` / `strings.Cut(req.ID, vaulttypes.RequestIDSeparator)` (as already done in `stripPrefixedVaultRequestID`), or at minimum replace `index+2` with `index+len(vaulttypes.RequestIDSeparator)`.
- Add unit tests that fail if `RequestIDSeparator`'s length changes without a corresponding update to the stripping logic.
- Document explicitly why the prefix-stripping exists (JSON-RPC 2.0 spec compliance) and add a defensive check/log if the owner-derived string unexpectedly contains the separator.

### Proof of Concept
1. Change `RequestIDSeparator` from `"::"` to a single-character or 3+-character delimiter (a plausible future refactor, since it's just a string constant with no length invariant enforced anywhere).
2. Leave the two `index+2` call sites in `handler.go` unmodified (there is nothing forcing a developer to notice them, since they are string-literal offsets not derived from the constant).
3. Send a gateway vault request; the gateway internally prefixes the response ID as `owner<separator>requestID`.
4. Observe that `resp.ID[index+2:]` / `req.ID[index+2:]` slices at the wrong byte offset, returning a request ID to the user that is either missing leading characters of the true request ID or includes trailing separator characters — producing a JSON-RPC response whose `id` field does not match the client's original request `id`, violating JSON-RPC 2.0 and potentially causing the calling client's response-matching logic to misassociate the response.

### Citations

**File:** core/capabilities/vault/vaulttypes/types.go (L34-35)
```go
	// RequestIDSeparator is used to separate parts(owner, user-provided-requestId) of the request ID.
	RequestIDSeparator = "::"
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L278-281)
```go
	originalRequestID := req.ID
	authorizedOwner := authResult.AuthorizedOwner()
	prefixedRequestID := authorizedOwner + vaulttypes.RequestIDSeparator + originalRequestID
	req.ID = prefixedRequestID
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L305-311)
```go
func stripPrefixedVaultRequestID(requestID string) (originalRequestID, prefixedOwner string) {
	prefixedOwner, originalRequestID, ok := strings.Cut(requestID, vaulttypes.RequestIDSeparator)
	if !ok {
		return requestID, ""
	}
	return originalRequestID, prefixedOwner
}
```

**File:** core/services/gateway/handlers/vault/handler.go (L588-591)
```go
	index := strings.Index(resp.ID, vaulttypes.RequestIDSeparator)
	if index != -1 {
		resp.ID = resp.ID[index+2:]
	}
```

**File:** core/services/gateway/handlers/vault/handler.go (L787-790)
```go
	index := strings.Index(req.ID, vaulttypes.RequestIDSeparator)
	if index != -1 {
		req.ID = req.ID[index+2:]
	}
```
