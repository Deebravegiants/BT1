# [M] Openstack Manila Persistent XSS in Metadata field

## Summary
Severity: Medium
Advisory: GHSA-vq76-5ghr-9p4v
CVE: CVE-2016-6519
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-vq76-5ghr-9p4v
Type: github-advisory

## Affected
- PyPI: `manila-ui` — affected >=0 <2.5.1

## Details
Cross-site scripting (XSS) vulnerability in the "Shares" overview in Openstack Manila before 2.5.1 allows remote authenticated users to inject arbitrary web script or HTML via the Metadata field in the "Create Share" form.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-6519
- https://github.com/openstack/manila-ui/commit/009913d725bee34cef0bd62e47a298025ace2696
- https://github.com/openstack/manila-ui/commit/89593686ef18f2bd06223b92071b4be2362a5abd
- https://github.com/openstack/manila-ui/commit/fca19a1b0d42536644212c5d673fbd6866e67c43
- https://bugs.launchpad.net/manila-ui/+bug/1597738
- https://bugzilla.redhat.com/show_bug.cgi?id=1375147
- http://rhn.redhat.com/errata/RHSA-2016-2115.html
- http://rhn.redhat.com/errata/RHSA-2016-2116.html
- http://rhn.redhat.com/errata/RHSA-2016-2117.html
- http://www.openwall.com/lists/oss-security/2016/09/15/7
- http://www.securityfocus.com/bid/93001
