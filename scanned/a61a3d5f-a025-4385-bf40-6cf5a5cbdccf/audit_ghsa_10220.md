# [M] Helm Chart extraction output directory collapse via `Chart.yaml` name dot-segment

## Summary
Severity: Medium
Advisory: GHSA-hr2v-4r36-88hr
CVE: CVE-2026-35206
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:N/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-hr2v-4r36-88hr
Type: github-advisory

## Affected
- Go: `helm.sh/helm/v4` — affected >=0 <4.1.4
- Go: `helm.sh/helm/v3` — affected >=0 <3.20.2

## Details
Helm is a package manager for Charts for Kubernetes. In Helm versions <=3.20.1 and <=4.1.3, a specially crafted Chart will cause `helm pull --untar  [chart URL | repo/chartname]` to write the Chart's contents to the immediate output directory (as defaulted to the current working directory; or as given by the `--destination` and `--untardir` flags), rather than the expected output directory suffixed by the chart's name.

### Impact

The bug enables writing the Chart's contents (unpackaged/untar'ed) to the output directory `<output dir>/`, instead of the expected `<output dir>/<chart name>/`, potentially overwriting the contents of the targeted directory.

Note: a chart name containing POSIX dot-dot, or dot-dot and slashes (as if to refer to parent directories) do not resolve beyond the output directory as designed.

### Patches

This issue has been resolved in Helm v3.20.2 and v4.1.3

A Chart with an unexpected name (those specified to be "." or ".."), or a Chart name which results in a non-unique directory will be rejected.

### Workarounds

Ensure the the name of the Chart does not comprise/contain POSIX pathname special directory references ie. dot-dot ("..") or dot ("."). In addition, ensuring that the `pull --untar` flag (or equivalent SDK option) refers to a unique/empty output directory prevents chart extraction from inadvertently overwriting existing files within the specified directory.

### Credits

Oleh Konko
@1seal

## References
- https://github.com/helm/helm/security/advisories/GHSA-hr2v-4r36-88hr
- https://nvd.nist.gov/vuln/detail/CVE-2026-35206
- https://github.com/helm/helm/commit/4e7994d4467182f535b6797c94b5b0e994a91436
- https://github.com/helm/helm
- https://github.com/helm/helm/releases/tag/v4.1.4
