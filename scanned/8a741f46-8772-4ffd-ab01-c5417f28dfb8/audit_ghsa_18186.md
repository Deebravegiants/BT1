# [H] Dragonfly doesn't have authentication enabled for some Manager’s endpoints

## Summary
Severity: High
Advisory: GHSA-89vc-vf32-ch59
CVE: CVE-2025-59345
CWE: CWE-287, CWE-306
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-09-17
Source: https://github.com/advisories/GHSA-89vc-vf32-ch59
Type: github-advisory

## Affected
- Go: `github.com/dragonflyoss/dragonfly` — affected >=0 <2.1.0
- Go: `d7y.io/dragonfly/v2` — affected >=0 <2.1.0

## Details
### Impact
The /api/v1/jobs and /preheats endpoints in Manager web UI are accessible without authentication. Any user with network access to the Manager can create, delete, and modify jobs, and create preheat jobs.

An unauthenticated adversary with network access to a Manager web UI uses /api/v1/jobs endpoint to create hundreds of useless jobs. The Manager is in a denial-of-service state, and stops accepting requests from valid administrators.

### Patches

- Dragonfy v2.1.0 and above.

### Workarounds

There are no effective workarounds, beyond upgrading.

### References

A third party security audit was performed by Trail of Bits, you can see the [full report](https://github.com/dragonflyoss/dragonfly/blob/main/docs/security/dragonfly-comprehensive-report-2023.pdf).

If you have any questions or comments about this advisory, please email us at [dragonfly-maintainers@googlegroups.com](mailto:dragonfly-maintainers@googlegroups.com).

## References
- https://github.com/dragonflyoss/dragonfly/security/advisories/GHSA-89vc-vf32-ch59
- https://nvd.nist.gov/vuln/detail/CVE-2025-59345
- https://github.com/dragonflyoss/dragonfly
- https://github.com/dragonflyoss/dragonfly/blob/main/docs/security/dragonfly-comprehensive-report-2023.pdf
- https://pkg.go.dev/vuln/GO-2025-3965
