# [H] Jellysweep uses uncontrolled data in image cache API endpoint

## Summary
Severity: High
Advisory: GHSA-xc93-q32j-cpcg
CVE: CVE-2025-64178
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H (CVSS_V4)
Published: 2025-11-04
Source: https://github.com/advisories/GHSA-xc93-q32j-cpcg
Type: github-advisory

## Affected
- Go: `github.com/jon4hz/jellysweep` — affected >=0 <0.13.0

## Details
### Impact
The `/api/images/cache` which is used to download media posters from the server accepted an `url` parameter, which was directly passed to the cache package and that downloaded the poster from this URL.
This URL parameter can be used to make the jellysweep server download arbitrary content.

The API endpoint can only be used by authenticated users.

### Patches

Fixed in `v0.13.0`. The affected (and now fixed) library was also moved to `internal/` because it wasn't meant to be imported.


### References
https://github.com/jon4hz/jellysweep/security/code-scanning/28

## References
- https://github.com/jon4hz/jellysweep/security/advisories/GHSA-xc93-q32j-cpcg
- https://nvd.nist.gov/vuln/detail/CVE-2025-64178
- https://github.com/jon4hz/jellysweep/commit/17466312510966418aea941e4944229856d55101
- https://github.com/jon4hz/jellysweep
