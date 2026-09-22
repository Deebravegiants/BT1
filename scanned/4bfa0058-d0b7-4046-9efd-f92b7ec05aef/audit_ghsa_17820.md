# [M] Karmada Tar Slips in CRDs archive extraction

## Summary
Severity: Medium
Advisory: GHSA-cwrh-575j-8vr3
CVE: CVE-2024-56514
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-01-03
Source: https://github.com/advisories/GHSA-cwrh-575j-8vr3
Type: github-advisory

## Affected
- Go: `github.com/karmada-io/karmada` — affected >=0 <1.12.0

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

Both in karmadactl and karmada-operator, it is possible to supply a filesystem path, or an HTTP(s) URL to retrieve the custom resource definitions(CRDs) needed by karmada. The CRDs are downloaded as a gzipped tarfile and are vulnerable to a TarSlip vulnerability. An attacker able to supply a malicious CRD file into a karmada initialization could write arbitrary files in arbitrary paths of the filesystem.

### Patches
_Has the problem been patched? What versions should users upgrade to?_

From karmada version v1.12.0, when processing custom CRDs files, CRDs archive verification is utilized to enhance file system robustness.

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

When using `karmadactl init` to set up Karmada, if you need to set flag `--crd` to customize the CRD files required for karmada initialization, you can manually inspect the CRD files to check whether they contain sequences such as `../` that would alter file paths, to determine if they potentially include malicious files. 

When using karmada-operator to set up Karmada, you must upgrade your karmada-operator to one of the fixed versions.

### References
_Are there any links users can visit to find out more?_

1. Enhancements made from the Karmada community: https://github.com/karmada-io/karmada/pull/5713, https://github.com/karmada-io/karmada/pull/5703

## References
- https://github.com/karmada-io/karmada/security/advisories/GHSA-cwrh-575j-8vr3
- https://nvd.nist.gov/vuln/detail/CVE-2024-56514
- https://github.com/karmada-io/karmada/pull/5703
- https://github.com/karmada-io/karmada/pull/5713
- https://github.com/karmada-io/karmada/commit/40ec488b18a461ab0f871d2c9ec8665b361f0d50
- https://github.com/karmada-io/karmada/commit/f78e7e2a3d02bed04e9bc7abd3ae7b3ac56862d2
- https://github.com/karmada-io/karmada
