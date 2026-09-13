# [M] OpenStack Cinder Exposure of Sensitive Information to an Unauthorized Actor vulnerability

## Summary
Severity: Medium
Advisory: GHSA-qhch-g8qr-p497
CVE: CVE-2014-3641
CWE: CWE-200
Ecosystem: PyPI
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-qhch-g8qr-p497
Type: github-advisory

## Affected
- PyPI: `cinder` — affected >=0 <2014.1.3

## Details
The (1) GlusterFS and (2) Linux Smbfs drivers in OpenStack Cinder before 2014.1.3 allows remote authenticated users to obtain file data from the Cinder-volume host by cloning and attaching a volume with a crafted qcow2 header.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3641
- https://access.redhat.com/errata/RHSA-2014:1787
- https://access.redhat.com/errata/RHSA-2014:1788
- https://access.redhat.com/security/cve/CVE-2014-3641
- https://bugs.launchpad.net/cinder/+bug/1350504
- https://bugzilla.redhat.com/show_bug.cgi?id=1141996
- https://opendev.org/openstack/cinder
- https://web.archive.org/web/20200228053848/http://www.securityfocus.com/bid/70221
- http://rhn.redhat.com/errata/RHSA-2014-1787.html
- http://rhn.redhat.com/errata/RHSA-2014-1788.html
- http://seclists.org/oss-sec/2014/q4/78
- http://www.ubuntu.com/usn/USN-2405-1
