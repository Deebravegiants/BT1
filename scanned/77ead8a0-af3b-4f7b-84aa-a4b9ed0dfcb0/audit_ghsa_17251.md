# [H] openshift-apiserver: SSRF via Missing IP/Network-Range Validation in User-Supplied Image References

## Summary
Severity: High
Advisory: GHSA-gxvv-45f6-3ch8
CVE: CVE-2025-14443
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:L (CVSS_V3)
Published: 2025-12-16
Source: https://github.com/advisories/GHSA-gxvv-45f6-3ch8
Type: github-advisory

## Affected
- Go: `github.com/openshift/openshift-apiserver` — affected 4.0.0-alpha.0
- Go: `github.com/openshift/openshift-apiserver` — affected >=0

## Details
A flaw was found in ose-openshift-apiserver. This vulnerability allows internal network enumeration, service discovery, limited information disclosure, and potential Denial of Service (DoS) through Server-Side Request Forgery (SSRF) due to missing IP address and network-range validation when processing user-supplied image references.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-14443
- https://github.com/openshift/openshift-apiserver/pull/591
- https://github.com/openshift/openshift-apiserver/pull/599
- https://access.redhat.com/security/cve/CVE-2025-14443
- https://bugzilla.redhat.com/show_bug.cgi?id=2420964
- https://github.com/openshift/openshift-apiserver
