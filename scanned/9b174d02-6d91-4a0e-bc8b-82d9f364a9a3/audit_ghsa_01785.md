# [M] Denial of Service in OpenShift Origin

## Summary
Severity: Medium
Advisory: GHSA-rf3m-mhv7-x39f
CVE: CVE-2015-5250
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2021-12-20
Source: https://github.com/advisories/GHSA-rf3m-mhv7-x39f
Type: github-advisory

## Affected
- Go: `github.com/openshift/origin` — affected >=0 <1.0.6

## Details
The API server in OpenShift Origin 1.0.5 allows remote attackers to cause a denial of service (master process crash) via crafted JSON data

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-5250
- https://github.com/openshift/origin/issues/4374
- https://github.com/openshift/origin/commit/dace5075e31b74703e944b6b3ebe8836be8d1b9a
- https://access.redhat.com/errata/RHSA-2015:1736
- https://access.redhat.com/security/cve/CVE-2015-5250
- https://bugzilla.redhat.com/show_bug.cgi?id=1259867
- https://web.nvd.nist.gov/view/vuln/detail?vulnId=CVE-2015-5250
