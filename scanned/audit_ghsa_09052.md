# [H] OpenTelemetry eBPF Instrumentation: MongoDB parser panics on malformed wire messages

## Summary
Severity: High
Advisory: GHSA-j8p6-96vp-f3r9
CVE: CVE-2026-45685
CWE: CWE-20, CWE-248, CWE-704
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-j8p6-96vp-f3r9
Type: github-advisory

## Affected
- Go: `go.opentelemetry.io/obi` — affected >=0 <0.9.0

## Details
### Summary

Malformed MongoDB wire messages can trigger uncaught panics in the MongoDB TCP parser, allowing a remote unauthenticated attacker to crash the telemetry agent and cause a denial of service. The parser operates on raw attacker-controlled network payloads before the input is fully validated, so a single crafted message can terminate telemetry collection for the affected process or node.

### Details

MongoDB parsing support was introduced by commit `2070f568a` (`Add Initial support for mongodb`), so the explicit released version minimum affected is `v0.1.0`.

There are two related panic conditions in released `go.opentelemetry.io/obi` versions:

- In `v0.1.0` through `v0.3.0`, `parseOpMessage` reads OP_MSG flag bits from `buf[msgHeaderSize:msgHeaderSize+int32Size]` without first ensuring the buffer is at least `msgHeaderSize + int32Size` bytes long. A truncated OP_MSG packet can therefore trigger a slice-bounds panic before the parser returns an error.
- In `v0.1.0` through `v0.3.0`, `parseSections` consumes the section type byte and then reads the document-sequence length from `buf[offSet:offSet+int32Size]` without re-validating that enough bytes remain after the type byte. A malformed document-sequence section can therefore trigger another slice-bounds panic.
- In `v0.1.0` through `v0.8.0`, `parseFirstField` assumes the collection name for collection-scoped commands is always a string and performs an unchecked type assertion on `field.Value`. A malformed BSON document can therefore trigger a runtime panic with `interface conversion` instead of returning a parse error.

The bounds-check panic was fixed by commit `3aa58cdaaa97fbb72f8ef4c3609ae425aacaf8bb` (`Fix MongoDB client panic`), which first appears in release `v0.4.0`. The unchecked BSON type assertion is still present in `v0.8.0`.

Because this code runs while decoding attacker-controlled MongoDB traffic, the failure mode is process termination rather than graceful rejection of invalid input. In deployments where the telemetry agent monitors traffic from untrusted or partially trusted clients, a single malformed packet can terminate collection until the agent is restarted.

Affected code paths are in `pkg/ebpf/common/mongo_detect_transform.go` and correspond to `parseOpMessage`, `parseSections`, and `parseFirstField`.

### PoC

The following reproductions are fully self-contained. They create a temporary test file inside an affected checkout and then run `go test` against the real parser code in the repository.

1. Reproduce the `v0.1.0` through `v0.3.0` bounds-check panics:

   ```bash
   git clone https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation.git obi-poc
   cd obi-poc
   git checkout v0.3.0

   cat > pkg/ebpf/common/mongo_security_poc_test.go <<'EOF'
   package ebpfcommon

   import "testing"

   func TestSecurityPoCParseOpMessageShortPanics(t *testing.T) {
	   parseOpMessage(make([]byte, 16), 0, false, nil)
   }

   func TestSecurityPoCParseSectionsShortDocSequencePanics(t *testing.T) {
	   parseSections([]byte{byte(sectionTypeDocumentSequence), 0x01, 0x02, 0x03})
   }
   EOF

   go test ./pkg/ebpf/common -run 'TestSecurityPoCParseOpMessageShortPanics|TestSecurityPoCParseSectionsShortDocSequencePanics' -count=1
   ```

   Expected result:

   - `TestSecurityPoCParseOpMessageShortPanics` panics with a message similar to `slice bounds out of range [:20] with capacity 16`
   - `TestSecurityPoCParseSectionsShortDocSequencePanics` panics with a message similar to `slice bounds out of range [:5] with capacity 4`

1. Reproduce the `v0.1.0` through `v0.8.0` unchecked BSON type-assertion panic:

   ```bash
   git clone https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation.git obi-poc
   cd obi-poc
   git checkout v0.8.0

   cat > pkg/ebpf/common/mongo_security_poc_test.go <<'EOF'
   package ebpfcommon

   import (
	   "testing"

	   "go.mongodb.org/mongo-driver/v2/bson"
   )

   func TestSecurityPoCParseFirstFieldTypeAssertionPanics(t *testing.T) {
	   parseFirstField(bson.E{Key: commFind, Value: int32(123)})
   }
   EOF

   go test ./pkg/ebpf/common -run TestSecurityPoCParseFirstFieldTypeAssertionPanics -count=1
   ```

   Expected result: panic with a message similar to `interface conversion: interface {} is int32, not string`.

### Impact

This is a remote denial-of-service vulnerability in the MongoDB protocol parser. Any deployment that enables MongoDB parsing and processes attacker-controlled or malformed MongoDB traffic is impacted. Successful exploitation lets an unauthenticated attacker crash the telemetry agent by sending a crafted OP_MSG packet or malformed BSON document, causing loss of observability until the process is restarted.

## References
- https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation/security/advisories/GHSA-j8p6-96vp-f3r9
- https://nvd.nist.gov/vuln/detail/CVE-2026-45685
- https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation
- https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation/releases/tag/v0.9.0
