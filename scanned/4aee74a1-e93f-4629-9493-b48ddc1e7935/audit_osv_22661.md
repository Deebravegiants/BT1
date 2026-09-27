# [C] Improper object validation allows for arbitrary code execution in GitOps Tools Extension for VSCode

## Summary
Severity: Critical
Advisory: CVE-2022-35975
Aliases: GHSA-873x-829r-gxcp
CVSS: 9.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H)
Published: 2022-08-18
Source: https://osv.dev/vulnerability/CVE-2022-35975
Type: osv

## Details
The GitOps Tools Extension for VSCode can make it easier to manage Flux objects. A specially crafted Flux object may allow for remote code execution in the machine running the extension, in the context of the user that is running VSCode. Users using the VSCode extension to manage clusters that are shared amongst other users are affected by this issue. The only safe mitigation is to update to the latest version of the extension.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/35xxx/CVE-2022-35975.json
- https://github.com/weaveworks/vscode-gitops-tools/security/advisories/GHSA-873x-829r-gxcp
- https://nvd.nist.gov/vuln/detail/CVE-2022-35975
