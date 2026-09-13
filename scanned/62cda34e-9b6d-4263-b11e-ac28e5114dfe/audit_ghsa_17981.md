# [M] Helm May Panic Due To Incorrect YAML Content

## Summary
Severity: Medium
Advisory: GHSA-f9f8-9pmf-xv68
CVE: CVE-2025-55198
CWE: CWE-908
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-08-14
Source: https://github.com/advisories/GHSA-f9f8-9pmf-xv68
Type: github-advisory

## Affected
- Go: `helm.sh/helm/v3` — affected >=0 <3.18.5

## Details
A Helm contributor discovered an improper validation of type error when parsing Chart.yaml and index.yaml files that can lead to a panic.

### Impact

There are two areas of YAML validation that were impacted. First, when a `Chart.yaml` file had a `null` maintainer or the `child` or `parent` of a dependencies `import-values` could be parsed as something other than a string, `helm lint` would panic. Second, when an `index.yaml` had an empty entry in the list of chart versions Helm would panic on interactions with that repository.

### Patches

This issue has been resolved in Helm v3.18.5.

### Workarounds

Ensure YAML files are formatted as Helm expects prior to processing them with Helm.

### References

Helm's security policy is spelled out in detail in our [SECURITY](https://github.com/helm/community/blob/master/SECURITY.md) document.

### Credits

Disclosed by Jakub Ciolek at AlphaSense.

## References
- https://github.com/helm/helm/security/advisories/GHSA-f9f8-9pmf-xv68
- https://nvd.nist.gov/vuln/detail/CVE-2025-55198
- https://github.com/helm/helm/commit/ec5f59e2db56533d042a124f5bae54dd87b558e6
- https://github.com/helm/helm
