# [M] Ella Core has a Denial of Service via SCTP connection cleanup deadlock 

## Summary
Severity: Medium
Advisory: GHSA-9h59-p45g-445h
CVE: CVE-2026-33904
CWE: CWE-833
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-9h59-p45g-445h
Type: github-advisory

## Affected
- Go: `github.com/ellanetworks/core` — affected >=0 <1.7.0

## Details
## Summary

A deadlock in the AMF's SCTP notification handler causes the entire AMF control plane to hang until the process is restarted. 

## Impact

An attacker with access to the N2 interface can cause Ella Core to hang, resulting in a denial of service for all subscribers.

## Fix

Add deferred Radio cleanup in serveConn SCTP server so that every connection exit path removes the radio. Remove the stale-entry scan from SCTP Notification handling.

## References
- https://github.com/ellanetworks/core/security/advisories/GHSA-9h59-p45g-445h
- https://nvd.nist.gov/vuln/detail/CVE-2026-33904
- https://github.com/ellanetworks/core/commit/999f606c5cae261471d9e3f063d7ecd1bd754076
- https://github.com/ellanetworks/core
- https://github.com/ellanetworks/core/releases/tag/v1.7.0
