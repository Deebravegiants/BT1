# [C] Helm Improper Certificate Validation

## Summary
Severity: Critical
Advisory: GHSA-x6r5-vxfg-gq3v
CVE: CVE-2019-1010275
CWE: CWE-295
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-x6r5-vxfg-gq3v
Type: github-advisory

## Affected
- Go: `helm.sh/helm` — affected >=0 <2.7.2

## Details
helm Before 2.7.2 is affected by: CWE-295: Improper Certificate Validation. The impact is: Unauthorized clients could connect to the server because self-signed client certs were aloowed. The component is: helm (many files updated, see https://github.com/helm/helm/pull/3152/files/1096813bf9a425e2aa4ac755b6c991b626dfab50). The attack vector is: A malicious client could connect to the server over the network. The fixed version is: 2.7.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1010275
- https://github.com/helm/helm/pull/3152
- https://github.com/helm/helm/pull/3152/files/1096813bf9a425e2aa4ac755b6c991b626dfab50
- https://github.com/helm/helm/commit/1096813bf9a425e2aa4ac755b6c991b626dfab50
- https://github.com/helm/helm/releases/tag/v2.7.2
