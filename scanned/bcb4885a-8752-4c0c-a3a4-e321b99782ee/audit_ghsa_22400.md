# [H] Bazaar allows remote attackers to execute arbitrary commands via a bzr+ssh URL with initial dash character in hostname

## Summary
Severity: High
Advisory: GHSA-jjxg-hpm7-g95f
CVE: CVE-2017-14176
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-jjxg-hpm7-g95f
Type: github-advisory

## Affected
- PyPI: `bzr` — affected >=0

## Details
Bazaar through 2.7.0, when Subprocess SSH is used, allows remote attackers to execute arbitrary commands via a bzr+ssh URL with an initial dash character in the hostname, a related issue to CVE-2017-9800, CVE-2017-12836, CVE-2017-12976, CVE-2017-16228, CVE-2017-1000116, and CVE-2017-1000117.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-14176
- https://bugs.debian.org/874429
- https://bugs.launchpad.net/bzr/+bug/1710979
- https://bugzilla.redhat.com/show_bug.cgi?id=1486685
- https://bugzilla.suse.com/show_bug.cgi?id=1058214
- https://github.com/pypa/advisory-database/tree/main/vulns/bzr/PYSEC-2017-149.yaml
- https://www.debian.org/security/2017/dsa-4052
- http://people.canonical.com/~ubuntu-security/cve/2017/CVE-2017-14176.html
- http://www.ubuntu.com/usn/usn-3411-1
