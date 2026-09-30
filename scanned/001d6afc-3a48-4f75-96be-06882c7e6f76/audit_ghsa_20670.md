# [M] python-oslo-utils has improper password parsing

## Summary
Severity: Medium
Advisory: GHSA-wmqq-r32m-87c5
CVE: CVE-2022-0718
CWE: CWE-522, CWE-532
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-08-29
Source: https://github.com/advisories/GHSA-wmqq-r32m-87c5
Type: github-advisory

## Affected
- PyPI: `oslo-utils` — affected >=0 <4.10.1

## Details
A flaw was found in python-oslo-utils. Due to improper parsing, passwords with a double quote ( " ) in them cause incorrect masking in debug logs, causing any part of the password after the double quote to be plaintext

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0718
- https://access.redhat.com/errata/RHSA-2022:0993
- https://access.redhat.com/errata/RHSA-2022:8873
- https://access.redhat.com/security/cve/CVE-2022-0718
- https://bugs.launchpad.net/oslo.utils/+bug/1949623
- https://bugzilla.redhat.com/show_bug.cgi?id=2056850
- https://github.com/advisories/GHSA-wmqq-r32m-87c5
- https://github.com/openstack/oslo.utils
- https://github.com/pypa/advisory-database/tree/main/vulns/oslo-utils/PYSEC-2022-258.yaml
- https://lists.debian.org/debian-lts-announce/2022/09/msg00015.html
- https://opendev.org/openstack/oslo.utils/commit/6e17ae1f7959c64dfd20a5f67edf422e702426aa
- https://security-tracker.debian.org/tracker/CVE-2022-0718
