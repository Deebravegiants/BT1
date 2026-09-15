# [M] Improper Input Validation in Docker Engine

## Summary
Severity: Medium
Advisory: GHSA-qrrc-ww9x-r43g
CVE: CVE-2020-13401
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-qrrc-ww9x-r43g
Type: github-advisory

## Affected
- Go: `github.com/docker/docker-ce` — affected >=0 <19.03.11

## Details
An issue was discovered in Docker Engine before 19.03.11. An attacker in a container, with the CAP_NET_RAW capability, can craft IPv6 router advertisements, and consequently spoof external IPv6 hosts, obtain sensitive information, or cause a denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13401
- https://docs.docker.com/engine/release-notes
- https://github.com/docker/docker-ce/releases/tag/v19.03.11
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/DN4JQAOXBE3XUNK3FD423LHE3K74EMJT
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/KJZLKRCOJMOGUIJI2AS27BOZS3RBEF3K
- https://security.gentoo.org/glsa/202008-15
- https://security.netapp.com/advisory/ntap-20200717-0002
- https://www.debian.org/security/2020/dsa-4716
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00040.html
- http://www.openwall.com/lists/oss-security/2020/06/01/5
