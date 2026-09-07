# [M] OpenShift Builder has a path traversal, allows command injection in privileged BuildContainer

## Summary
Severity: Medium
Advisory: GHSA-qqv8-ph7f-h3f7
CVE: CVE-2024-7387
CWE: CWE-250
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-09-17
Source: https://github.com/advisories/GHSA-qqv8-ph7f-h3f7
Type: github-advisory

## Affected
- Go: `github.com/openshift/builder` — affected >=0

## Details
A flaw was found in openshift/builder. This vulnerability allows command injection via path traversal, where a malicious user can execute arbitrary commands on the OpenShift node running the builder container. When using the "Docker" strategy, executable files inside the privileged build container can be overridden using the `spec.source.secrets.secret.destinationDir` attribute of the `BuildConfig` definition. An attacker running code in a privileged container could escalate their permissions on the node running the container.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-7387
- https://github.com/openshift/builder/commit/0b62633adfa2836465202bc851885e078ec888d1
- https://access.redhat.com/errata/RHSA-2024:3718
- https://access.redhat.com/errata/RHSA-2024:6122
- https://access.redhat.com/errata/RHSA-2024:6685
- https://access.redhat.com/errata/RHSA-2024:6687
- https://access.redhat.com/errata/RHSA-2024:6689
- https://access.redhat.com/errata/RHSA-2024:6691
- https://access.redhat.com/errata/RHSA-2024:6705
- https://access.redhat.com/security/cve/CVE-2024-7387
- https://bugzilla.redhat.com/show_bug.cgi?id=2302259
- https://github.com/openshift/builder
- https://pkg.go.dev/vuln/GO-2024-3129
- https://stuxxn.github.io/advisory/2024/10/02/openshift-build-docker-priv-esc.html
