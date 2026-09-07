# [M] Incus has Unbounded YAML Metadata Decode via Parsing

## Summary
Severity: Medium
Advisory: GHSA-67wx-r9xr-x75x
CVE: CVE-2026-41648
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:L (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-67wx-r9xr-x75x
Type: github-advisory

## Affected
- Go: `github.com/lxc/incus/v6/cmd/incusd` — affected >=0

## Details
### Summary
User provided image and backup tarballs would be unpacked and YAML files parsed without any size restrictions. This was making it easy for an authenticated user to provide a crafted image or backup tarball that when parsed by Incus would lead to a very large YAML document being loaded into memory, potentially causing the entire server to run out of memory.

### Details
It was found that getImageMetadata and backup.GetInfo call yaml.NewDecoder(tr).Decode() directly on the tar reader without limiting how many bytes the YAML decoder can consume. The tar entry hdr.Size is not checked before decoding.

A tar archive can be crafted in which metadata.yaml or backup/index.yaml declares a large size in the tar header, causing the YAML decoder to read and allocate proportional memory on the server. The gopkg.in/yaml.v2 library mitigates YAML alias and anchor bombs, such as “billion laughs,” through its built-in excessive-aliasing check. However, large flat YAML documents with many keys or long string values can still produce linear but amplified memory consumption of approximately 5x to 6x the input size.

A 200 MB tar entry for metadata.yaml may cause approximately 1.2 GB of heap allocations during decode, which may be sufficient to trigger an out-of-memory condition on a constrained daemon or significantly degrade service. Because the decode occurs in the daemon process, excessive garbage-collection pressure can affect concurrent operations. Appropriate API permissions are required to upload an image or backup archive.

Mitigating factors include the fact that the amplification is linear rather than exponential, at approximately 5x to 6x, and that upload bandwidth is the practical bottleneck for delivering large payloads.

Affected Files:
 - https://github.com/lxc/incus/blob/v6.22.0/cmd/incusd/images.go#L1456
 - https://github.com/lxc/incus/blob/v6.22.0/internal/server/backup/backup_info.go#L87
 - https://github.com/lxc/incus/blob/v6.22.0/internal/server/backup/backup_info.go#L115

Image metadata parsing reads YAML directly from the tar stream:
Affected Code:
```
if hdr.Name == "metadata.yaml" || hdr.Name == "./metadata.yaml" {
    err = yaml.NewDecoder(tr).Decode(&result)
```

Backup info parsing does the same:

Affected Code:
```
if hdr.Name == backupIndexPath {
    err = yaml.NewDecoder(tr).Decode(&result)

if result.Config == nil && hdr.Name == "backup/container/backup.yaml" {
    err = yaml.NewDecoder(tr).Decode(&result.Config)
```

This was confirmed as follows:

Command:
```
go test ./test/fuzz -run='TestUnboundedYAMLMetadataDecode' -count=1 -v
```

Output:
```
=== RUN   TestUnboundedYAMLMetadataDecode
   image_metadata_poc_test.go:80: metadata.yaml size: 10.2 MB
   image_metadata_poc_test.go:113: metadata.yaml hdr.Size = 10688940 bytes (10.2 MB) -- no size
       check exists in getImageMetadata before yaml.NewDecoder(tr).Decode()
   image_metadata_poc_test.go:124: decoded 50000 properties from 10.2 MB metadata.yaml
   image_metadata_poc_test.go:125: yaml.NewDecoder(tr).Decode() accepted 10.2 MB metadata.yaml
       with 50000 properties -- no hdr.Size check or io.LimitReader in images.go:1457 or
       backup_info.go:88
--- FAIL: TestUnboundedYAMLMetadataDecode (0.11s)
FAIL
```

It is recommended to add a size check on hdr.Size before YAML decoding and to wrap the tar reader in io.LimitReader.

Proposed Fix:
```
const maxMetadataSize = 1 << 20 // 1 MB

if hdr.Size > maxMetadataSize {
    return nil, fmt.Errorf("metadata entry too large: %d bytes", hdr.Size)
}

err = yaml.NewDecoder(io.LimitReader(tr, maxMetadataSize)).Decode(&result)
```

A patch is available at https://github.com/lxc/incus/releases/tag/v7.0.0.

### Credit
This issue was discovered and reported by the team at 7asecurity (https://7asecurity.com/)

## References
- https://github.com/lxc/incus/security/advisories/GHSA-67wx-r9xr-x75x
- https://nvd.nist.gov/vuln/detail/CVE-2026-41648
- https://github.com/lxc/incus
- https://github.com/lxc/incus/releases/tag/v7.0.0
