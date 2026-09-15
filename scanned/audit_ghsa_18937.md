# [M] OpenStack's Mistral Client has a local file inclusion vulnerability

## Summary
Severity: Medium
Advisory: GHSA-75hx-6r6j-hw56
CVE: CVE-2021-4472
CWE: CWE-73
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-11-26
Source: https://github.com/advisories/GHSA-75hx-6r6j-hw56
Type: github-advisory

## Affected
- PyPI: `python-mistralclient` — affected >=0 <4.3.0

## Details
The mistral-dashboard plugin for openstack has a local file inclusion vulnerability through the 'Create Workbook' feature that may result in disclosure of arbitrary local files content.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-4472
- https://access.redhat.com/security/cve/CVE-2021-4472
- https://bugs.launchpad.net/horizon/+bug/1931558
- https://bugzilla.redhat.com/show_bug.cgi?id=2417321
- https://lists.debian.org/debian-lts-announce/2025/12/msg00002.html
- https://lists.debian.org/debian-lts-announce/2025/12/msg00003.html
- https://opendev.org/openstack/mistral-dashboard
- https://review.opendev.org/c/openstack/mistral-dashboard/+/800952
- https://review.opendev.org/c/openstack/python-mistralclient/+/800950
