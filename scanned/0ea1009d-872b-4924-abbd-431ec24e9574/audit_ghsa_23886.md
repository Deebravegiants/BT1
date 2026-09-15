# [M] OpenStack Compute (Nova)'s VMWare driver vulnerable to denial of service

## Summary
Severity: Medium
Advisory: GHSA-92hc-c226-32q7
CVE: CVE-2014-3608
Ecosystem: PyPI
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-92hc-c226-32q7
Type: github-advisory

## Affected
- PyPI: `nova` — affected >=0 <2014.1.3

## Details
The VMWare driver in OpenStack Compute (Nova) before 2014.1.3 allows remote authenticated users to bypass the quota limit and cause a denial of service (resource consumption) by putting the VM into the rescue state, suspending it, which puts into an ERROR state, and then deleting the image.  NOTE: this vulnerability exists because of an incomplete fix for CVE-2014-2573.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3608
- https://access.redhat.com/errata/RHSA-2014:1781
- https://access.redhat.com/errata/RHSA-2014:1782
- https://access.redhat.com/security/cve/CVE-2014-3608
- https://bugs.launchpad.net/nova/+bug/1338830
- https://bugzilla.redhat.com/show_bug.cgi?id=1148253
- https://opendev.org/openstack/nova
- https://web.archive.org/web/20200228053850/http://www.securityfocus.com/bid/70220
- http://rhn.redhat.com/errata/RHSA-2014-1781.html
- http://rhn.redhat.com/errata/RHSA-2014-1782.html
- http://seclists.org/oss-sec/2014/q4/65
- http://www.securityfocus.com/bid/70220
