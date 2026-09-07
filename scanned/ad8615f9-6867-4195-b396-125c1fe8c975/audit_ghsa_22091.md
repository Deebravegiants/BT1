# [H] SoSReport Predictable Tmp File Names

## Summary
Severity: High
Advisory: GHSA-3g56-2hh3-35ph
CVE: CVE-2015-7529
CWE: CWE-59
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-3g56-2hh3-35ph
Type: github-advisory

## Affected
- PyPI: `sosreport` — affected >=3.0 <3.3

## Details
sosreport in SoS 3.x allows local users to obtain sensitive information from sosreport files or gain privileges via a symlink attack on an archive file in a temporary directory, as demonstrated by `sosreport-$hostname-$date.tar` in `/tmp/sosreport-$hostname-$date`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-7529
- https://github.com/sosreport/sos/issues/696
- https://access.redhat.com/errata/RHSA-2016:0152
- https://access.redhat.com/errata/RHSA-2016:0188
- https://access.redhat.com/security/cve/CVE-2015-7529
- https://bugzilla.redhat.com/show_bug.cgi?id=1282542
- https://github.com/pypa/advisory-database/tree/main/vulns/sosreport/PYSEC-2017-73.yaml
- https://github.com/sosreport/sos
- https://web.archive.org/web/20160416033632/http://www.securityfocus.com/bid/83162
- http://rhn.redhat.com/errata/RHSA-2016-0152.html
- http://rhn.redhat.com/errata/RHSA-2016-0188.html
- http://www.ubuntu.com/usn/USN-2845-1
