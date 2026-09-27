# [H] Undertow Missing Authorization when requesting a protected directory without trailing slash

## Summary
Severity: High
Advisory: GHSA-w69w-jvc7-wjgv
CVE: CVE-2019-10184
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2019-08-01
Source: https://github.com/advisories/GHSA-w69w-jvc7-wjgv
Type: github-advisory

## Affected
- Maven: `io.undertow:undertow-servlet` — affected >=0 <2.0.23

## Details
undertow before version 2.0.23.Final is vulnerable to an information leak issue. Web apps may have their directory structures predicted through requests without trailing slashes via the api.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10184
- https://github.com/undertow-io/undertow/pull/794
- https://github.com/undertow-io/undertow/commit/5fa7ac68c0e4251c93056d9982db5e794e04ebfa
- https://access.redhat.com/errata/RHSA-2019:2935
- https://access.redhat.com/errata/RHSA-2019:2936
- https://access.redhat.com/errata/RHSA-2019:2937
- https://access.redhat.com/errata/RHSA-2019:2938
- https://access.redhat.com/errata/RHSA-2019:2998
- https://access.redhat.com/errata/RHSA-2019:3044
- https://access.redhat.com/errata/RHSA-2019:3045
- https://access.redhat.com/errata/RHSA-2019:3046
- https://access.redhat.com/errata/RHSA-2019:3050
- https://access.redhat.com/errata/RHSA-2020:0727
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10184
- https://issues.redhat.com/browse/UNDERTOW-1578
- https://security.netapp.com/advisory/ntap-20220210-0016
