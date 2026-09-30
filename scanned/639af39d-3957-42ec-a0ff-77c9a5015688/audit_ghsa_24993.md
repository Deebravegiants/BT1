# [M] OpenStack Cinder Denial of Service using XML entities 

## Summary
Severity: Medium
Advisory: GHSA-mfg4-9xf4-f45q
CVE: CVE-2013-4202
Ecosystem: PyPI
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-mfg4-9xf4-f45q
Type: github-advisory

## Affected
- PyPI: `cinder` — affected >=0 <7.0.0a0

## Details
The (1) backup (api/contrib/backups.py) and (2) volume transfer (contrib/volume_transfer.py) APIs in OpenStack Cinder Grizzly 2013.1.3 and earlier allows remote attackers to cause a denial of service (resource consumption and crash) via an XML Entity Expansion (XEE) attack.  NOTE: this issue is due to an incomplete fix for CVE-2013-1664.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4202
- https://bugs.launchpad.net/ossa/+bug/1190229
- https://github.com/openstack/cinder
- http://github.com/openstack/cinder/commit/2023eecc4b1a35daf42a64fa01967ed12c7d017b
- http://github.com/openstack/cinder/commit/4ad95dba4fccbbc0df923dea0dc9e5c3ac9f4cc2
- http://rhn.redhat.com/errata/RHSA-2013-1198.html
- http://www.ubuntu.com/usn/USN-2005-1
