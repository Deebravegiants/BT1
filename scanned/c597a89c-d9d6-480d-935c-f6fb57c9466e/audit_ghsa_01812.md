# [C] Authentication Bypass in dex

## Summary
Severity: Critical
Advisory: GHSA-2x32-jm95-2cpx
CVE: CVE-2020-27847
CWE: CWE-228, CWE-290
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-12-20
Source: https://github.com/advisories/GHSA-2x32-jm95-2cpx
Type: github-advisory

## Affected
- Go: `github.com/dexidp/dex` — affected >=0 <2.27.0

## Details
A vulnerability exists in the SAML connector of the github.com/dexidp/dex library used to process SAML Signature Validation. This flaw allows an attacker to bypass SAML authentication. The highest threat from this vulnerability is to confidentiality, integrity, as well as system availability. This flaw affects dex versions before 2.27.0.

## References
- https://github.com/dexidp/dex/security/advisories/GHSA-m9hp-7r99-94h5
- https://nvd.nist.gov/vuln/detail/CVE-2020-27847
- https://bugzilla.redhat.com/show_bug.cgi?id=1907732
- https://mattermost.com/blog/coordinated-disclosure-go-xml-vulnerabilities
