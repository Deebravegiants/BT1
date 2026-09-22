# [H] VelaUX APIServer vulnerable to Authentication Bypass by Capture-replay

## Summary
Severity: High
Advisory: CVE-2022-36089
Aliases: GHSA-cq42-w295-r29q
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:N)
Published: 2022-09-07
Source: https://osv.dev/vulnerability/CVE-2022-36089
Type: osv

## Details
KubeVela is an application delivery platform Users using KubeVela's VelaUX APIServer could be affected by an authentication bypass vulnerability. In KubeVela prior to versions 1.4.11 and 1.5.4, VelaUX APIServer uses the `PlatformID` as the signed key to generate the JWT tokens for users. Another API called `getSystemInfo` exposes the platformID. This vulnerability allows users to use the platformID to re-generate the JWT tokens to bypass the authentication. Versions 1.4.11 and 1.5.4 contain a patch for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/36xxx/CVE-2022-36089.json
- https://github.com/kubevela/kubevela/security/advisories/GHSA-cq42-w295-r29q
- https://nvd.nist.gov/vuln/detail/CVE-2022-36089
- https://github.com/kubevela/kubevela/pull/4634
