# [C] ChainerRL Visualizer 0.1.1 vulnerable to Path Traversal via unsafe use of send_file function

## Summary
Severity: Critical
Advisory: GHSA-687h-86vc-5x59
CVE: CVE-2022-31573
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:L (CVSS_V3)
Published: 2022-07-12
Source: https://github.com/advisories/GHSA-687h-86vc-5x59
Type: github-advisory

## Affected
- PyPI: `chainerrl-visualizer` — affected >=0

## Details
The chainer/chainerrl-visualizer repository through 0.1.1 on GitHub allows absolute path traversal because the Flask send_file function is used unsafely.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-31573
- https://github.com/github/securitylab/issues/669#issuecomment-1117265726
- https://github.com/chainer/chainerrl-visualizer
