# [H] rdiffweb does not have a rate limit on incorrect password attempts to prevent brute force attacks

## Summary
Severity: High
Advisory: GHSA-9g3v-v24q-jj5p
CVE: CVE-2022-3273
CWE: CWE-326, CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-10-06
Source: https://github.com/advisories/GHSA-9g3v-v24q-jj5p
Type: github-advisory

## Affected
- PyPI: `rdiffweb` — affected >=0 <2.5.0

## Details
rdiffweb prior to 2.5.0a4 does not have a rate limit to prevent attackers attempting brute force attacks to guess passwords. Version 2.5.0a4 limits the number of incorrect password attempts.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3273
- https://github.com/ikus060/rdiffweb/commit/b5e3bb0a98268d18ceead36ab9b2b7eaacd659a8
- https://github.com/ikus060/rdiffweb
- https://github.com/pypa/advisory-database/tree/main/vulns/rdiffweb/PYSEC-2022-43156.yaml
- https://huntr.dev/bounties/a6df4bad-3382-4add-8918-760d885690f6
