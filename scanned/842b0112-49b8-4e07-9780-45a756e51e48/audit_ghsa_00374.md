# [H] Insufficiently Protected Credentials in Requests

## Summary
Severity: High
Advisory: GHSA-x84v-xcm2-53pg
CVE: CVE-2018-18074
CWE: CWE-522
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-10-29
Source: https://github.com/advisories/GHSA-x84v-xcm2-53pg
Type: github-advisory

## Affected
- PyPI: `requests` — affected >=0 <2.20.0

## Details
The Requests package through 2.19.1 before 2018-09-14 for Python sends an HTTP Authorization header to an http URI upon receiving a same-hostname https-to-http redirect, which makes it easier for remote attackers to discover credentials by sniffing the network.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-18074
- https://github.com/requests/requests/issues/4716
- https://github.com/requests/requests/pull/4718
- https://github.com/requests/requests/commit/c45d7c49ea75133e52ab22a8e9e13173938e36ff
- https://access.redhat.com/errata/RHSA-2019:2035
- https://bugs.debian.org/910766
- https://github.com/pypa/advisory-database/tree/main/vulns/requests/PYSEC-2018-28.yaml
- https://github.com/requests/requests
- https://usn.ubuntu.com/3790-1
- https://usn.ubuntu.com/3790-2
- https://www.oracle.com/security-alerts/cpujul2022.html
- http://docs.python-requests.org/en/master/community/updates/#release-and-version-history
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00024.html
