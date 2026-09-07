# [M] SmallRye Health UI Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-pvc3-wvxr-7cmf
CVE: CVE-2021-3914
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-08-26
Source: https://github.com/advisories/GHSA-pvc3-wvxr-7cmf
Type: github-advisory

## Affected
- Maven: `io.smallrye:smallrye-health-ui` — affected >=0 <3.1.2

## Details
It was found that the smallrye health metrics UI component did not properly sanitize some user inputs. An attacker could use this flaw to conduct cross-site scripting attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3914
- https://github.com/smallrye/smallrye-health/pull/333
- https://github.com/smallrye/smallrye-health/commit/01b25a038824887363cd413d8cd14052f5fc3541
- https://github.com/smallrye/smallrye-health/commit/47a33f19f5bb1e4216a15f3aee6ca3b1e2ccba59
- https://access.redhat.com/security/cve/CVE-2021-3914
- https://bugzilla.redhat.com/show_bug.cgi?id=2018015
- https://github.com/smallrye/smallrye-health
