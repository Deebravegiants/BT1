# [M] Kruise allows leveraging the kruise-daemon pod to list all secrets in the entire cluster

## Summary
Severity: Medium
Advisory: GHSA-437m-7hj5-9mpw
CVE: CVE-2023-30617
CWE: CWE-250, CWE-269
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-01-05
Source: https://github.com/advisories/GHSA-437m-7hj5-9mpw
Type: github-advisory

## Affected
- Go: `github.com/openkruise/kruise` — affected >=0.8.0 <1.3.1
- Go: `github.com/openkruise/kruise` — affected >=1.4.0 <1.4.1
- Go: `github.com/openkruise/kruise` — affected >=1.5.0 <1.5.2

## Details
### Impact
Attacker that has gain root privilege of the node that kruise-daemon run , can leverage the kruise-daemon pod to list all secrets in the entire cluster. After that, attackers can leverage the "captured" secrets (e.g. the kruise-manager service account token) to gain extra privilege such as pod modification. 

### Workarounds
For users that do not require imagepulljob functions, they can modify kruise-daemon-role to drop the cluster level secret get/list privilege 

### Patches

For users who're using v0.8.x ~ v1.2.x, please update the v1.3.1
For users who're using v1.3, please update the v1.3.1
For users who're using v1.4, please update the v1.4.1
For users who're using v1.5, please update the v1.5.2
### References
None

## References
- https://github.com/openkruise/kruise/security/advisories/GHSA-437m-7hj5-9mpw
- https://nvd.nist.gov/vuln/detail/CVE-2023-30617
- https://github.com/openkruise/kruise
