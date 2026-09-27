# [M] free5GC AMF: Missing default case in Content-Type switch in HTTPUEContextTransfer

## Summary
Severity: Medium
Advisory: GHSA-r99v-75p9-xqm5
CVE: CVE-2026-41136
CWE: CWE-440
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-r99v-75p9-xqm5
Type: github-advisory

## Affected
- Go: `github.com/free5gc/amf` — affected >=0

## Details
## Summary

The `HTTPUEContextTransfer` handler in `internal/sbi/api_communication.go` does not include a `default` case in the `Content-Type` switch statement. When a request arrives with an unsupported `Content-Type`, the deserialization step is silently skipped, `err` remains `nil`, and the processor is invoked with a completely uninitialized `UeContextTransferRequest` object.

## Details

In `internal/sbi/api_communication.go`, the `HTTPUEContextTransfer` function handles the `Content-Type` header with a switch statement that only covers `application/json` and `multipart/related`:

```go
switch str[0] {
case applicationjson:
    err = openapi.Deserialize(ueContextTransferRequest.JsonData, requestBody, contentType)
case multipartrelate:
    err = openapi.Deserialize(&ueContextTransferRequest, requestBody, contentType)
// no default case
}

if err != nil {
    // skipped entirely when Content-Type is unsupported
    c.JSON(http.StatusBadRequest, rsp)
    return
}

s.Processor().HandleUEContextTransferRequest(c, ueContextTransferRequest)
```

This is inconsistent with the two analogous handlers in the same file, `HTTPCreateUEContext` and `HTTPN1N2MessageTransfer`, which both correctly include a `default` branch:

```go
default:
    err = fmt.Errorf("wrong content type")
```

The fix is simply to add the same `default` case to `HTTPUEContextTransfer`.

## PoC

With a free5GC deployment running, send a POST request to the UE context transfer endpoint using any unsupported `Content-Type` (e.g. `text/plain`):

```bash
curl -s -X POST "http://<AMF_IP>/namf-comm/v1/ue-contexts/<ueContextId>/transfer" \\
  -H "Content-Type: text/plain" \\
  -d '{"test":"data"}' \\
  -i
```

**Expected (correct) behavior:** `400 Bad Request` from the SBI layer, rejecting the request due to unsupported Content-Type — consistent with `HTTPCreateUEContext`.

**Actual (observed) behavior:** The SBI-layer error check is bypassed and the processor is reached with an empty request object, returning:

```
HTTP/1.1 400 Bad Request
{"status": 400, "cause": "MANDATORY_IE_MISSING"}
```

The `MANDATORY_IE_MISSING` cause originates from the processor's internal validation, not from the SBI handler — confirming the processor was called with an uninitialized struct.

## Impact

The endpoint is an inter-NF SBI API used during AMF-to-AMF UE context handover. It is not directly reachable from external UEs and requires access to the internal 5GC SBI network. The processor's secondary mandatory field validation prevents any unintended state modification, so there is no direct exploitability. However, the SBI handler layer is the intended first line of defense — relying on the processor to compensate for a missing input check increases fragility and violates defense in depth. Any future change to the processor's validation logic could inadvertently expose the system to processing completely empty request objects.

## References
- https://github.com/free5gc/free5gc/security/advisories/GHSA-r99v-75p9-xqm5
- https://nvd.nist.gov/vuln/detail/CVE-2026-41136
- https://github.com/free5gc/amf/releases/tag/v1.4.3
- https://github.com/free5gc/free5gc
