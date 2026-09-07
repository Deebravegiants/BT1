# [M] OpenStack Dashboard (aka Horizon) vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-cmg8-5c63-pg95
CVE: CVE-2014-0157
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-cmg8-5c63-pg95
Type: github-advisory

## Affected
- PyPI: `horizon` — affected >=2013.2 <2013.2.4

## Details
Cross-site scripting (XSS) vulnerability in the Horizon Orchestration dashboard in OpenStack Dashboard (aka Horizon) 2013.2 before 2013.2.4 and icehouse before icehouse-rc2 allows remote attackers to inject arbitrary web script or HTML via the description field of a Heat template.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-0157
- https://access.redhat.com/errata/RHSA-2014:0581
- https://access.redhat.com/security/cve/CVE-2014-0157
- https://bugzilla.redhat.com/show_bug.cgi?id=1082858
- https://launchpad.net/bugs/1289033
- https://opendev.org/openstack/horizon
- https://web.archive.org/web/20200228185211/http://www.securityfocus.com/bid/66706
- http://lists.opensuse.org/opensuse-updates/2015-01/msg00040.html
- http://www.openwall.com/lists/oss-security/2014/04/08/8
