# [C] Authorization bypass in Openshift

## Summary
Severity: Critical
Advisory: GHSA-m3fm-h5jp-q79p
CVE: CVE-2016-1906
CWE: CWE-285
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-12-20
Source: https://github.com/advisories/GHSA-m3fm-h5jp-q79p
Type: github-advisory

## Affected
- Go: `github.com/openshift/origin` — affected >=0 <1.1.1

## Details
Openshift allows remote attackers to gain privileges by updating a build configuration that was created with an allowed type to a type that is not allowed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-1906
- https://github.com/openshift/origin/issues/6556
- https://github.com/openshift/origin/pull/6576
- https://github.com/openshift/origin/commit/d95ec085f03ecf10e8c424a4f0340ddb38891406
- https://access.redhat.com/errata/RHSA-2016:0070
- https://access.redhat.com/errata/RHSA-2016:0351
- https://access.redhat.com/security/cve/CVE-2016-1906
- https://bugzilla.redhat.com/show_bug.cgi?id=1297916
- https://web.nvd.nist.gov/view/vuln/detail?vulnId=CVE-2016-1906
