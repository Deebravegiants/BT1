# [M] Re-creating a deleted user in lakeFS will re-enable previous user credentials that existed prior to its deletion

## Summary
Severity: Medium
Advisory: GHSA-hh33-46q4-hwm2
CVE: CVE-2024-43784
CWE: CWE-281, CWE-287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2024-11-26
Source: https://github.com/advisories/GHSA-hh33-46q4-hwm2
Type: github-advisory

## Affected
- Go: `github.com/treeverse/lakefs` — affected >=0 <1.33.0

## Details
### Impact
Existing lakeFS users who have issued credentials to users who have been deleted.
Creating a new user with the same username, that user will inherit all of the previous user's credentials lakeFS needs to delete user credentials upon user deletion.

### Patches
_Has the problem been patched? What versions should users upgrade to?_

### Workarounds
A possible workaround will be not to reuse usernames that were previously deleted

### References
_Are there any links users can visit to find out more?_

## References
- https://github.com/treeverse/lakeFS/security/advisories/GHSA-hh33-46q4-hwm2
- https://nvd.nist.gov/vuln/detail/CVE-2024-43784
- https://github.com/treeverse/lakeFS
- https://github.com/treeverse/lakeFS/releases/tag/v1.33.0
