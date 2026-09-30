# [C] Remote unauthenticated attackers able to upload files in Onionshare

## Summary
Severity: Critical
Advisory: GHSA-7g47-xxff-9p85
CVE: CVE-2021-41868
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-11-19
Source: https://github.com/advisories/GHSA-7g47-xxff-9p85
Type: github-advisory

## Affected
- PyPI: `onionshare-cli` — affected >=2.3 <2.4

## Details
OnionShare 2.3 before 2.4 allows remote unauthenticated attackers to upload files on a non-public node when using the --receive functionality.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-41868
- https://github.com/onionshare/onionshare/issues/1396
- https://github.com/onionshare/onionshare/pull/1404
- https://github.com/onionshare/onionshare
- https://www.ihteam.net/advisory/onionshare
