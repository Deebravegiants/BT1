# [H] Podman's incorrect handling of the supplementary groups may lead to data disclosure, modification

## Summary
Severity: High
Advisory: GHSA-4wjj-jwc9-2x96
CVE: CVE-2022-2989
CWE: CWE-842, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-09-14
Source: https://github.com/advisories/GHSA-4wjj-jwc9-2x96
Type: github-advisory

## Affected
- Go: `github.com/containers/podman/v4` — affected >=0 <4.2.0
- Go: `github.com/containers/podman/v3` — affected >=0 <3.0.1

## Details
An incorrect handling of the supplementary groups in the Podman container engine might lead to the sensitive information disclosure or possible data modification if an attacker has direct access to the affected container where supplementary groups are used to set access permissions and is able to execute a binary code in that container.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-2989
- https://github.com/containers/podman/pull/15618
- https://github.com/containers/podman/pull/15677
- https://github.com/containers/podman/pull/15696
- https://access.redhat.com/errata/RHSA-2022:7822
- https://access.redhat.com/errata/RHSA-2022:8008
- https://access.redhat.com/errata/RHSA-2022:8431
- https://access.redhat.com/security/cve/CVE-2022-2989
- https://bugzilla.redhat.com/show_bug.cgi?id=2121445
- https://github.com/containers/podman
- https://www.benthamsgaze.org/2022/08/22/vulnerability-in-linux-containers-investigation-and-mitigation
