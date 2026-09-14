I found a concrete analog: `StringToAlignedBytes` in the gateway's node-handshake authentication path silently truncates over-length identifiers into a fixed-size buffer with no length validation, exactly matching the CVE-2019-13164 bug class (unbounded name written into a fixed-size buffer, enabling identifier confusion/collision that bypasses an intended check).

### Title
Unvalidated DON ID / Gateway ID length in gateway handshake auth header allows silent truncation and identifier collision - ([File: core/services/gateway/common/utils.go])

### Summary
`StringToAlignedBytes` copies an attacker/node-supplied string into a fixed-size byte buffer without ever validating that the input is within the target buffer size. Two distinct `DonID`/`GatewayID` values that share a common prefix of length `size` become byte-identical after alignment, and the signed/parsed value silently loses everything beyond `size` bytes — mirroring the CVE-2019-13164 root cause (an unbounded name copied into `IFNAMSIZ`-sized buffer with no length check, causing distinct names to collide after truncation and defeat an ACL comparison).

### Finding Description
`StringToAlignedBytes` performs a `copy` into a `size`-length slice with no bounds check on the input string: [1](#0-0) 

This helper is used directly in the node-to-gateway handshake authentication protocol to pack `DonID` and `GatewayID` into fixed-size fields (`HandshakeDonIDLen`, `HandshakeGatewayURLLen`) before signing and verification: [2](#0-1) 

Unlike the analogous legacy Gateway `Message` path — which explicitly validates `DonID`/`Method`/`MessageID` length *before* alignment via `Validate()`: [3](#0-2) 

the handshake `PackAuthHeader`/`PackChallenge` functions perform no equivalent length check on `elems.DonID` or `elems.GatewayID` before calling `StringToAlignedBytes`. If either value exceeds `HandshakeDonIDLen` / `HandshakeGatewayURLLen`, the excess bytes are silently dropped by `copy`, and the signature is computed over the truncated (aligned) bytes, not the original string. On unpack, `AlignedBytesToString` returns only the truncated value (up to size or the first null byte): [4](#0-3) 

This means an unprivileged node/client that controls its own `DonID` or `GatewayID` string (e.g., a config-driven identifier) can craft a value whose first `HandshakeDonIDLen`/`HandshakeGatewayURLLen` bytes match a legitimate, different DON ID or Gateway ID, causing the handshake logic to treat the request as belonging to that other DON/Gateway once truncated and re-parsed — the exact "ACL bypass via un-bounded name causing collision after fixed-size truncation" pattern from CVE-2019-13164.

### Impact Explanation
If a node or connecting client can control the `DonID`/`GatewayID` string used to build the handshake auth header/challenge (e.g. via configuration), a crafted overlong value can collide (after truncation) with a different DON's/Gateway's identifier used elsewhere for routing/allowlisting decisions, potentially allowing cross-DON message routing/impersonation confusion within the gateway handshake layer. This is a request/identity confusion vector rather than a full authentication bypass, since a valid signature is still required, but it undermines the integrity of DON/Gateway identity binding within the signed handshake payload.

### Likelihood Explanation
Exploitability depends on whether `DonID`/`GatewayID` strings that reach `PackAuthHeader`/`PackChallenge` are attacker-influenced (e.g., derived from node TOML config or gateway config supplied by an operator with node-level but not gateway-admin privileges) and whether `HandshakeDonIDLen`/`HandshakeGatewayURLLen` are small enough to be practically collided. I was not able to fully verify from the retrieved code whether these values originate from trusted, gateway-signed configuration only, or whether an unprivileged node operator can set an arbitrary `DonID`/`GatewayID` string that reaches this packing function unchecked — this needs further verification of the config loading and node registration path.

### Recommendation
Add explicit length validation (reject rather than silently truncate) for `DonID` and `GatewayID` in `PackAuthHeader`/`PackChallenge` before calling `StringToAlignedBytes`, mirroring the length checks already present in `api.Message.Validate()`. Consider changing `StringToAlignedBytes` itself to return an error when `len(input) > size` instead of silently truncating, closing off this bug class for any future callers.

### Proof of Concept
1. Construct two distinct `DonID` values, `donA` and `donAXXXX...` (padded so they diverge only after `HandshakeDonIDLen` bytes), both longer than `HandshakeDonIDLen`.
2. Call `PackAuthHeader` with each — both produce identical aligned bytes for the `DonID` field because `StringToAlignedBytes` truncates silently: [1](#0-0) 
3. `UnpackSignedAuthHeader` on the receiving/gateway side will recover the same (truncated) `DonID` for both inputs via `AlignedBytesToString`: [5](#0-4) 
4. Any downstream logic keyed on the recovered `DonID` string (e.g., DON-based routing or acceptance decisions) cannot distinguish the two original values, demonstrating the truncation-driven identifier collision.

### Citations

**File:** core/services/gateway/common/utils.go (L21-26)
```go
// input string can't have any 0x0 characters
func StringToAlignedBytes(input string, size int) []byte {
	aligned := make([]byte, size)
	copy(aligned, input)
	return aligned
}
```

**File:** core/services/gateway/common/utils.go (L28-34)
```go
func AlignedBytesToString(data []byte) string {
	idx := slices.IndexFunc(data, func(b byte) bool { return b == 0 })
	if idx == -1 {
		return string(data)
	}
	return string(data[:idx])
}
```

**File:** core/services/gateway/network/handshake.go (L68-97)
```go
func PackAuthHeader(elems *AuthHeaderElems) []byte {
	packed := common.Uint32ToBytes(elems.Timestamp)
	packed = append(packed, common.StringToAlignedBytes(elems.DonID, HandshakeDonIDLen)...)
	packed = append(packed, common.StringToAlignedBytes(elems.GatewayID, HandshakeGatewayURLLen)...)
	return packed
}

func UnpackSignedAuthHeader(data []byte) (elems *AuthHeaderElems, signer []byte, err error) {
	if len(data) != HandshakeAuthHeaderLen {
		return nil, nil, fmt.Errorf("auth header length is invalid (expected: %d, got: %d)", HandshakeAuthHeaderLen, len(data))
	}
	elems = &AuthHeaderElems{}
	offset := 0
	elems.Timestamp = common.BytesToUint32(data[offset : offset+HandshakeTimestampLen])
	offset += HandshakeTimestampLen
	elems.DonID = common.AlignedBytesToString(data[offset : offset+HandshakeDonIDLen])
	offset += HandshakeDonIDLen
	elems.GatewayID = common.AlignedBytesToString(data[offset : offset+HandshakeGatewayURLLen])
	offset += HandshakeGatewayURLLen
	signature := data[offset:]
	signer, err = common.ExtractSigner(signature, data[:len(data)-HandshakeSignatureLen])
	return elems, signer, err
}

func PackChallenge(elems *ChallengeElems) []byte {
	packed := common.Uint32ToBytes(elems.Timestamp)
	packed = append(packed, common.StringToAlignedBytes(elems.GatewayID, HandshakeGatewayURLLen)...)
	packed = append(packed, elems.ChallengeBytes...)
	return packed
}
```

**File:** core/services/gateway/api/message.go (L73-81)
```go
	if len(m.Body.DonID) == 0 || len(m.Body.DonID) > MessageDonIDMaxLen {
		return errors.New("invalid DON ID length")
	}
	if strings.HasSuffix(m.Body.DonID, NullChar) {
		return errors.New("DON ID ending with null bytes")
	}
	if len(m.Body.Receiver) != 0 && len(m.Body.Receiver) != MessageReceiverLen {
		return errors.New("invalid Receiver length")
	}
```
