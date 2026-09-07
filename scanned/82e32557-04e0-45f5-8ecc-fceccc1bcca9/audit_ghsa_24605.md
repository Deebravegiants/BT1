# [H] JSON-Patch Out-of-bounds Write vulnerability

## Summary
Severity: High
Advisory: GHSA-gxhv-3hwf-wjp9
CVE: CVE-2018-14632
CWE: CWE-787
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-gxhv-3hwf-wjp9
Type: github-advisory

## Affected
- Go: `github.com/evanphx/json-patch` — affected >=0 <0.5.2
- Go: `github.com/evanphx/json-patch` — affected >=3.0.0 <3.0.1-0.20180525145409-4c9aadca8f89

## Details
An out of bound write can occur when patching an Openshift object using the `oc patch` functionality in OpenShift Container Platform before 3.7. An attacker can use this flaw to cause a denial of service attack on the Openshift master api service which provides cluster management.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-14632
- https://github.com/evanphx/json-patch/pull/57
- https://github.com/evanphx/json-patch/commit/4c9aadca8f89e349c999f04e28199e96e81aba03
- https://github.com/evanphx/json-patch/commit/4c9aadca8f89e349c999f04e28199e96e81aba03#diff-65c563bba473be9d94ce4d033f74810e
- https://access.redhat.com/errata/RHBA-2018:2652
- https://access.redhat.com/errata/RHSA-2018:2654
- https://access.redhat.com/errata/RHSA-2018:2709
- https://access.redhat.com/errata/RHSA-2018:2906
- https://access.redhat.com/errata/RHSA-2018:2908
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-14632
- https://github.com/evanphx/json-patch
- https://pkg.go.dev/vuln/GO-2021-0076
