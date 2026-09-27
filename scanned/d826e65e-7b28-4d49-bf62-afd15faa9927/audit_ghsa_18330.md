# [M] Dragonfly incorrectly handles a task structure’s usedTrac field

## Summary
Severity: Medium
Advisory: GHSA-2qgr-gfvj-qpcr
CVE: CVE-2025-59348
CWE: CWE-457
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-09-17
Source: https://github.com/advisories/GHSA-2qgr-gfvj-qpcr
Type: github-advisory

## Affected
- Go: `github.com/dragonflyoss/dragonfly` — affected >=0 <2.1.0
- Go: `d7y.io/dragonfly/v2` — affected >=0 <2.1.0

## Details
### Impact
The processPieceFromSource method (figure 4.1) is part of a task processing mechanism. The method writes pieces of data to storage, updating a Task structure along the way. The method does not update the structure’s usedTraffic field, because an uninitialized variable n is used as a guard to the AddTraffic method call, instead of the result.Size variable.

```golang
var n int64
result.Size, err = pt.GetStorage().WritePiece([skipped])
result.FinishTime = time.Now().UnixNano()
if n > 0 {
       pt.AddTraffic(uint64(n))
}
```

A task is processed by a peer. The usedTraffic metadata is not updated during the processing. Rate limiting is incorrectly applied, leading to a denial-of-service condition for the peer.

### Patches

- Dragonfy v2.1.0 and above.

### Workarounds

There are no effective workarounds, beyond upgrading.

### References

A third party security audit was performed by Trail of Bits, you can see the [full report](https://github.com/dragonflyoss/dragonfly/blob/main/docs/security/dragonfly-comprehensive-report-2023.pdf).

If you have any questions or comments about this advisory, please email us at [dragonfly-maintainers@googlegroups.com](mailto:dragonfly-maintainers@googlegroups.com).

## References
- https://github.com/dragonflyoss/dragonfly/security/advisories/GHSA-2qgr-gfvj-qpcr
- https://nvd.nist.gov/vuln/detail/CVE-2025-59348
- https://github.com/dragonflyoss/dragonfly
- https://github.com/dragonflyoss/dragonfly/blob/main/docs/security/dragonfly-comprehensive-report-2023.pdf
- https://pkg.go.dev/vuln/GO-2025-3963
