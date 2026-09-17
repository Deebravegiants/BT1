# [M] Information disclosure in podman

## Summary
Severity: Medium
Advisory: GHSA-c3wv-qmjj-45r6
CVE: CVE-2020-14370
CWE: CWE-200, CWE-212
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-04-24
Source: https://github.com/advisories/GHSA-c3wv-qmjj-45r6
Type: github-advisory

## Affected
- Go: `github.com/containers/podman/v2` — affected >=0 <2.0.5

## Details
An information disclosure vulnerability was found in containers/podman in versions before 2.0.5. When using the deprecated Varlink API or the Docker-compatible REST API, if multiple containers are created in a short duration, the environment variables from the first container will get leaked into subsequent containers. An attacker who has control over the subsequent containers could use this flaw to gain access to sensitive information stored in such variables.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-14370
- https://github.com/containers/podman/commit/a7e864e6e7de894d4edde4fff00e53dc6a0b5074
- https://bugzilla.redhat.com/show_bug.cgi?id=1874268
- https://github.com/containers/podman
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/G6BPCZX4ASKNONL3MSCK564IVXNYSKLP
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/Y74V7HGQBNLT6XECCSNZNFZIB7G7XSAR
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/Z4Y2FSGQWP4AFT5AZ6UBN6RKHVXUBRFV
