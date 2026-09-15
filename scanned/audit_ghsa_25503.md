# [H] Podman publishes a malicious image to public registries

## Summary
Severity: High
Advisory: GHSA-66vw-v2x9-hw75
CVE: CVE-2022-1227
CWE: CWE-269, CWE-281
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-30
Source: https://github.com/advisories/GHSA-66vw-v2x9-hw75
Type: github-advisory

## Affected
- Go: `github.com/containers/podman/v3` — affected >=0 <3.4
- Go: `github.com/containers/psgo` — affected >=0 <1.7.2

## Details
Podman is a tool for managing OCI containers and pods. A privilege escalation flaw was found in Podman. This flaw allows an attacker to publish a malicious image to a public registry. Once this image is downloaded by a potential victim, the vulnerability is triggered after a user runs the 'podman top' command. This action gives the attacker access to the host filesystem, leading to information disclosure or denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-1227
- https://github.com/containers/podman/issues/10941
- https://github.com/containers/podman/pull/13862
- https://github.com/containers/podman/pull/13862/commits/79a3e149c10f74db4cebff624287385c90179d09
- https://github.com/containers/psgo/pull/92
- https://bugzilla.redhat.com/show_bug.cgi?id=2070368
- https://github.com/containers/podman
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DLUJZV3HBP56ADXU6QH2V7RNYUPMVBXQ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/DLUJZV3HBP56ADXU6QH2V7RNYUPMVBXQ
- https://pkg.go.dev/vuln/GO-2022-0558
- https://security.netapp.com/advisory/ntap-20240628-0001
