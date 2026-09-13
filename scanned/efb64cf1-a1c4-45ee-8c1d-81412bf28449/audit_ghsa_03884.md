# [C] Potential to access user credentials from the log files when debug logging enabled

## Summary
Severity: Critical
Advisory: GHSA-8vh8-vc28-m2hf
CVE: CVE-2019-10212
CWE: CWE-532
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-11-20
Source: https://github.com/advisories/GHSA-8vh8-vc28-m2hf
Type: github-advisory

## Affected
- Maven: `io.undertow:undertow-core` — affected >=0 <2.0.20

## Details
A flaw was found in, all under 2.0.20, in the Undertow DEBUG log for io.undertow.request.security. If enabled, an attacker could abuse this flaw to obtain the user's credentials from the log files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10212
- https://access.redhat.com/errata/RHSA-2019:2998
- https://access.redhat.com/errata/RHSA-2020:0727
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10212
- https://security.netapp.com/advisory/ntap-20220210-0017
