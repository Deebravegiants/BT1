# [M] Deis Workflow Manager race condition vulnerability

## Summary
Severity: Medium
Advisory: GHSA-jpfp-xq3p-4h3r
CVE: CVE-2016-15036
CWE: CWE-362
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2023-12-23
Source: https://github.com/advisories/GHSA-jpfp-xq3p-4h3r
Type: github-advisory

## Affected
- Go: `github.com/deis/workflow-manager` — affected >=0 <2.3.3

## Details
** UNSUPPORTED WHEN ASSIGNED ** A vulnerability was found in Deis Workflow Manager up to 2.3.2. It has been classified as problematic. This affects an unknown part. The manipulation leads to race condition. The complexity of an attack is rather high. The exploitability is told to be difficult. Upgrading to version 2.3.3 is able to address this issue. The patch is named 31fe3bccbdde134a185752e53380330d16053f7f. It is recommended to upgrade the affected component. The associated identifier of this vulnerability is VDB-248847. NOTE: This vulnerability only affects products that are no longer supported by the maintainer.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-15036
- https://github.com/deis/workflow-manager/pull/94
- https://github.com/deis/workflow-manager/commit/31fe3bccbdde134a185752e53380330d16053f7f
- https://github.com/deis/workflow-manager/releases/tag/v2.3.3
- https://vuldb.com/?ctiid.248847
- https://vuldb.com/?id.248847
