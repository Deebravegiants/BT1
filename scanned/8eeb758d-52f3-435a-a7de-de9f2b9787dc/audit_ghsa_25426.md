# [M] containernetworking/plugins vulnerable to MitM attacks

## Summary
Severity: Medium
Advisory: GHSA-fx6x-h9g4-56f8
CVE: CVE-2020-10749
CWE: CWE-300
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-fx6x-h9g4-56f8
Type: github-advisory

## Affected
- Go: `github.com/containernetworking/plugins` — affected >=0 <0.8.6

## Details
A vulnerability was found in all versions of containernetworking/plugins before version 0.8.6, that allows malicious containers in Kubernetes clusters to perform man-in-the-middle (MitM) attacks. A malicious container can exploit this flaw by sending rogue IPv6 router advertisements to the host or other containers, to redirect traffic to the malicious container.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-10749
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-10749
- https://github.com/containernetworking/plugins
- https://github.com/containernetworking/plugins/releases/tag/v0.8.6
- https://groups.google.com/forum/#!topic/kubernetes-security-announce/BMb_6ICCfp8
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/DV3HCDZYUTPPVDUMTZXDKK6IUO3JMGJC
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00063.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00065.html
