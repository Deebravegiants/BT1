# [M] OpenShift Assisted Installer leaks image pull secrets as plaintext in installation logs

## Summary
Severity: Medium
Advisory: GHSA-g8xm-p2h4-v6jp
CVE: CVE-2021-3684
CWE: CWE-532
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-03-24
Source: https://github.com/advisories/GHSA-g8xm-p2h4-v6jp
Type: github-advisory

## Affected
- Go: `github.com/openshift/assisted-installer` — affected >=0 <1.0.25.1

## Details
A vulnerability was found in OpenShift Assisted Installer. During generation of the Discovery ISO, image pull secrets were leaked as plaintext in the installation logs. An authenticated user could exploit this by re-using the image pull secret to pull container images from the registry as the associated user.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3684
- https://github.com/openshift/assisted-installer/commit/2403dad3795406f2c5d923af0894e07bc8b0bdc4
- https://github.com/openshift/assisted-installer/commit/f3800cfa3d64ce6dcd6f7b73f0578bb99bfdaf7a
- https://bugzilla.redhat.com/show_bug.cgi?id=1985962
- https://github.com/openshift/assisted-installer
