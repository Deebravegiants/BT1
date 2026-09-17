# [C] XML Processing error in github.com/crewjam/saml

## Summary
Severity: Critical
Advisory: GHSA-4hq8-gmxx-h6w9
CVE: CVE-2020-27846
CWE: CWE-115, CWE-287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-06-23
Source: https://github.com/advisories/GHSA-4hq8-gmxx-h6w9
Type: github-advisory

## Affected
- Go: `github.com/crewjam/saml` — affected >=0 <0.4.3

## Details
### Impact

There are three vulnerabilities in the go `encoding/xml` package that can allow an attacker to forge part of a signed XML document. For details on this vulnerability see [xml-roundtrip-validator](https://github.com/mattermost/xml-roundtrip-validator)

### Patches

In version 0.4.3, all XML input is validated prior to being parsed.

## References
- https://github.com/crewjam/saml/security/advisories/GHSA-4hq8-gmxx-h6w9
- https://nvd.nist.gov/vuln/detail/CVE-2020-27846
- https://github.com/crewjam/saml/commit/da4f1a0612c0a8dd0452cf8b3c7a6518f6b4d053
- https://bugzilla.redhat.com/show_bug.cgi?id=1907670
- https://github.com/crewjam/saml
- https://grafana.com/blog/2020/12/17/grafana-6.7.5-7.2.3-and-7.3.6-released-with-important-security-fix-for-grafana-enterprise
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/3YUTKIRWT6TWU7DS6GF3EOANVQBFQZYI
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ICP3YRY2VUCNCF2VFUSK77ZMRIC77FEM
- https://mattermost.com/blog/coordinated-disclosure-go-xml-vulnerabilities
- https://pkg.go.dev/vuln/GO-2021-0058
- https://security.netapp.com/advisory/ntap-20210205-0002
