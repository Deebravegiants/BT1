# [M] kyverno seccomp control can be circumvented

## Summary
Severity: Medium
Advisory: GHSA-33hq-f2mf-jm3c
CVE: CVE-2023-33191
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2023-05-25
Source: https://github.com/advisories/GHSA-33hq-f2mf-jm3c
Type: github-advisory

## Affected
- Go: `github.com/kyverno/kyverno` — affected >=1.9.2 <1.9.4

## Details
### Impact

Users of the podSecurity (`validate.podSecurity`) subrule in Kyverno versions v1.9.2 and v1.9.3 may be unable to enforce the check for the Seccomp control at the baseline level when using a `version` value of `latest`. There is no effect if a version number is referenced instead. See the [documentation](https://kyverno.io/docs/writing-policies/validate/#pod-security) for information on this subrule type. Users of Kyverno v1.9.2 and v1.9.3 are affected.

### Patches

v1.9.4
v1.10.0

### Workarounds

To work around this issue without upgrading to v1.9.4, temporarily install individual policies for the respective Seccomp checks in baseline [here](https://kyverno.io/policies/pod-security/baseline/restrict-seccomp/restrict-seccomp/) and restricted [here](https://kyverno.io/policies/pod-security/restricted/restrict-seccomp-strict/restrict-seccomp-strict/).

### References

* https://kyverno.io/docs/writing-policies/validate/#pod-security
* https://github.com/kyverno/kyverno/pull/7263

## References
- https://github.com/kyverno/kyverno/security/advisories/GHSA-33hq-f2mf-jm3c
- https://nvd.nist.gov/vuln/detail/CVE-2023-33191
- https://github.com/kyverno/kyverno/pull/7263
- https://github.com/kyverno/kyverno
- https://github.com/kyverno/kyverno/releases/tag/v1.9.4
