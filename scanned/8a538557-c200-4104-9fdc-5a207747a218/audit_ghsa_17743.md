# [H] Karmada PULL Mode Cluster Privilege Escalation

## Summary
Severity: High
Advisory: GHSA-mg7w-c9x2-xh7r
CVE: CVE-2024-56513
CWE: CWE-266
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-01-03
Source: https://github.com/advisories/GHSA-mg7w-c9x2-xh7r
Type: github-advisory

## Affected
- Go: `github.com/karmada-io/karmada` — affected >=0 <1.12.0

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

The [PULL](https://karmada.io/docs/next/userguide/clustermanager/cluster-registration#pull-mode) mode clusters registered with the `karmadactl register` command have excessive privileges to access control plane resources. By abusing these permissions, an attacker able to authenticate as the karmada-agent to a karmada cluster would be able to obtain administrative privileges over the entire federation system including all registered member clusters.


### Patches
_Has the problem been patched? What versions should users upgrade to?_

Since Karmada v1.12.0, command `karmadactl register` restricts the access permissions of pull mode member clusters to control plane resources. This way, an attacker able to authenticate as the karmada-agent cannot control other member clusters in Karmada.

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

Restricts the access permissions of pull mode member clusters to control plane resources according to [Karmada Component Permissions Docs](https://karmada.io/docs/administrator/security/component-permission).
### References
_Are there any links users can visit to find out more?_
 1. Enhancements made from the Karmada community: https://github.com/karmada-io/karmada/pull/5793
 2. Karmada Component Permissions: https://karmada.io/docs/administrator/security/component-permission

## References
- https://github.com/karmada-io/karmada/security/advisories/GHSA-mg7w-c9x2-xh7r
- https://nvd.nist.gov/vuln/detail/CVE-2024-56513
- https://github.com/karmada-io/karmada/pull/5793
- https://github.com/karmada-io/karmada/commit/2c82055c4c7f469411b1ba48c4dba4841df04831
- https://github.com/karmada-io/karmada
- https://karmada.io/docs/administrator/security/component-permission
