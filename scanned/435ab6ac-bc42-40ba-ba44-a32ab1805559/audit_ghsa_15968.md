# [M] Cilium's CIDR deny policies may not take effect when a more narrow CIDR allow is present

## Summary
Severity: Medium
Advisory: GHSA-3wwx-63fv-pfq6
CVE: CVE-2024-47825
CWE: CWE-1038, CWE-276
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2024-10-21
Source: https://github.com/advisories/GHSA-3wwx-63fv-pfq6
Type: github-advisory

## Affected
- Go: `github.com/cilium/cilium` — affected >=1.15.0 <1.15.10
- Go: `github.com/cilium/cilium` — affected >=1.14.0 <1.14.16

## Details
### Impact

A policy rule denying a prefix that is broader than /32 may be ignored if there is

- A policy rule referencing a more narrow prefix (`CIDRSet` or `toFQDN`) **and**
- This narrower policy rule specifies either `enableDefaultDeny: false` or `- toEntities: all`

Note that a rule specifying `toEntities: world` or `toEntities: 0.0.0.0/0` is insufficient, it must be to entity `all`.

As an example, given the below policies, traffic is allowed to 1.1.1.2, when it should be denied:

```
apiVersion: cilium.io/v2
kind: CiliumClusterwideNetworkPolicy
metadata:
  name: block-scary-range
spec:
  endpointSelector: {}
  egressDeny:
  - toCIDRSet:
    - cidr: 1.0.0.0/8

---

apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: evade-deny
spec:
  endpointSelector: {}
  egress:
  - toCIDR:
    - 1.1.1.2/32
  - toEntities:
    - all
```

### Patches

This issue affects:

- Cilium v1.14 between v1.14.0 and v1.14.15 inclusive
- Cilium v1.15 between v1.15.0 and v1.15.9 inclusive

This issue has been patched in:

- Cilium v1.14.16
- Cilium v1.15.10

### Workarounds

Users with policies using `enableDefaultDeny: false` can work around this issue by removing this configuration option and explicitly defining any allow rules required.

No workaround is available to users with egress policies that explicitly specify `toEntities: all`.

### Acknowledgements

The Cilium community has worked together with members of Isovalent to prepare these mitigations. Special thanks to @squeed, @christarazi, and @jrajahalme for their work in triaging and resolving this issue.

### For more information

If you have any questions or comments about this advisory, please reach out on [Slack](https://docs.cilium.io/en/latest/community/community/#slack).

If you think you have found a vulnerability affecting Cilium, we strongly encourage you to report it to our security mailing list at [security@cilium.io](mailto:security@cilium.io). This is a private mailing list for the Cilium security team, and your report will be treated with top priority.

## References
- https://github.com/cilium/cilium/security/advisories/GHSA-3wwx-63fv-pfq6
- https://nvd.nist.gov/vuln/detail/CVE-2024-47825
- https://github.com/cilium/cilium/commit/02d28d9ac9afcaddd301fae6fb4d6cda8c2d0c45
- https://github.com/cilium/cilium/commit/9c01afb5646af3f0c696421a410dc66c513b6524
- https://github.com/cilium/cilium
