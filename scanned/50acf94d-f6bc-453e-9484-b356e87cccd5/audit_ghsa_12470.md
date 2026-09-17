# [C] Improper Privilege Management in github.com/sap/cloud-security-client-go

## Summary
Severity: Critical
Advisory: GHSA-m8rw-rcpq-2vp2
CVE: CVE-2023-50424
CWE: CWE-269
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-12-13
Source: https://github.com/advisories/GHSA-m8rw-rcpq-2vp2
Type: github-advisory

## Affected
- Go: `github.com/sap/cloud-security-client-go` — affected >=0 <0.17.0

## Details
### Impact
SAP BTP Security Services Integration Library ([Golang] github.com/sap/cloud-security-client-go) allows under certain conditions an escalation of privileges. On successful exploitation, an unauthenticated attacker can obtain arbitrary permissions within the application.

### Patches
Upgrade to patched version >= 0.17.0
We always recommend to upgrade to the latest released version.

### Workarounds
No workarounds

### References
https://www.cve.org/CVERecord?id=CVE-2023-50424

## References
- https://github.com/SAP/cloud-security-client-go/security/advisories/GHSA-m8rw-rcpq-2vp2
- https://github.com/SAP/cloud-security-services-integration-library/security/advisories/GHSA-59c9-pxq8-9c73
- https://nvd.nist.gov/vuln/detail/CVE-2023-50424
- https://github.com/SAP/cloud-security-client-go/commit/2e3bd63e152e09f267316a1071034eb5d4b7f498
- https://blogs.sap.com/2023/12/12/unveiling-critical-security-updates-sap-btp-security-note-3411067
- https://github.com/SAP/cloud-security-client-go
- https://me.sap.com/notes/3411067
- https://pkg.go.dev/github.com/sap/cloud-security-client-go@v0.17.0
- https://www.sap.com/documents/2022/02/fa865ea4-167e-0010-bca6-c68f7e60039b.html
