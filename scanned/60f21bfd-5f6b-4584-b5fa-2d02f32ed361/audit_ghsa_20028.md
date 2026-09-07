# [M] nsupdate.info has Sensitive Cookie Without 'HttpOnly' Flag

## Summary
Severity: Medium
Advisory: GHSA-mwvp-qr62-cvjx
CVE: CVE-2019-25091
CWE: CWE-1004
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-12-28
Source: https://github.com/advisories/GHSA-mwvp-qr62-cvjx
Type: github-advisory

## Affected
- PyPI: `nsupdate` — affected >=0

## Details
A vulnerability classified as problematic has been found in nsupdate.info. This affects an unknown part of the file `src/nsupdate/settings/base.py` of the component `CSRF Cookie Handler`. The manipulation of the argument `CSRF_COOKIE_HTTPONLY` leads to cookie without `httponly` flag. It is possible to initiate the attack remotely. The name of the patch is 60a3fe559c453bc36b0ec3e5dd39c1303640a59a. It is recommended to apply a patch to fix this issue. The identifier VDB-216909 was assigned to this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-25091
- https://github.com/nsupdate-info/nsupdate.info/pull/410
- https://github.com/nsupdate-info/nsupdate.info/commit/60a3fe559c453bc36b0ec3e5dd39c1303640a59a
- https://github.com/nsupdate-info/nsupdate.info
- https://vuldb.com/?ctiid.216909
- https://vuldb.com/?id.216909
