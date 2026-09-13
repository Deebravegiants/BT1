# [H] OpenStack Cinder, Glance, and Nova contain Uncontrolled Resource Consumption

## Summary
Severity: High
Advisory: GHSA-g2j5-7vgx-6xrx
CVE: CVE-2015-5162
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-g2j5-7vgx-6xrx
Type: github-advisory

## Affected
- PyPI: `cinder` — affected >=0 <7.0.2
- PyPI: `cinder` — affected >=8.0.0 <9.0.0
- PyPI: `glance` — affected >=0 <14.0.0
- PyPI: `nova` — affected >=0 <12.0.4

## Details
The image parser in OpenStack Cinder prior to 7.0.2, and 8.0.0 and above, prior to 9.0.0; Glance prior to 14.00; and Nova prior to 12.0.4 does not properly limit qemu-img calls, which might allow attackers to cause a denial of service (memory and disk consumption) via a crafted disk image. This issue is patched in Cinder 7.0.2 and 9.0.0; Glance 14.0.0; and Nova 12.0.4

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-5162
- https://github.com/openstack/cinder/commit/455b318ced717fb38dfe40014817d78fbc47dea5
- https://github.com/openstack/glance/commit/69a9b659fd48aa3c1f84fc7bc9ae236b6803d31f
- https://github.com/openstack/nova/commit/6bc37dcceca823998068167b49aec6def3112397
- https://access.redhat.com/security/cve/CVE-2015-5162
- https://bugzilla.redhat.com/show_bug.cgi?id=1268303
- https://launchpad.net/bugs/1449062
- http://rhn.redhat.com/errata/RHSA-2016-2923.html
- http://rhn.redhat.com/errata/RHSA-2016-2991.html
- http://rhn.redhat.com/errata/RHSA-2017-0153.html
- http://rhn.redhat.com/errata/RHSA-2017-0156.html
- http://rhn.redhat.com/errata/RHSA-2017-0165.html
- http://rhn.redhat.com/errata/RHSA-2017-0282.html
- http://www.openwall.com/lists/oss-security/2016/10/06/8
- http://www.securityfocus.com/bid/76849
