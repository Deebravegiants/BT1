# [M] Horizon-Orchestration Cross-site scripting (XSS) vulnerability through resource name

## Summary
Severity: Medium
Advisory: GHSA-8vwv-2v7v-jmgr
CVE: CVE-2014-3473
CWE: CWE-79
Ecosystem: PyPI
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-8vwv-2v7v-jmgr
Type: github-advisory

## Affected
- PyPI: `horizon` — affected >=0 <8.0.0a0

## Details
Cross-site scripting (XSS) vulnerability in the Orchestration/Stack section in the Horizon Orchestration dashboard in OpenStack Dashboard (Horizon) before 2013.2.4, 2014.1 before 2014.1.2, and Juno before Juno-2, when used with Heat, allows remote Orchestration template owners or catalogs to inject arbitrary web script or HTML via a crafted template.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3473
- https://github.com/openstack/horizon/commit/c844bd692894353c60b320005b804970605e910f
- https://github.com/openstack/horizon/commit/de4466d88b816437fb29eff5ab23b9b964cd3985
- https://access.redhat.com/errata/RHSA-2014:0939
- https://access.redhat.com/errata/RHSA-2014:1188
- https://access.redhat.com/security/cve/CVE-2014-3473
- https://bugs.launchpad.net/horizon/+bug/1308727
- https://bugzilla.redhat.com/show_bug.cgi?id=1116090
- https://opendev.org/openstack/horizon
- http://lists.opensuse.org/opensuse-updates/2015-01/msg00040.html
- http://www.openwall.com/lists/oss-security/2014/07/08/6
- http://www.securityfocus.com/bid/68459
