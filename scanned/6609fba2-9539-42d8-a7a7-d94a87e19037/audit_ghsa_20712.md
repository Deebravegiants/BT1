# [H] Broken Authorization in ZITADEL Actions

## Summary
Severity: High
Advisory: GHSA-c8fj-4pm8-mp2c
CVE: CVE-2022-36051
CWE: CWE-436, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2022-08-30
Source: https://github.com/advisories/GHSA-c8fj-4pm8-mp2c
Type: github-advisory

## Affected
- Go: `github.com/zitadel/zitadel` — affected >=2.0.0 <2.2.0
- Go: `github.com/zitadel/zitadel` — affected >=1.42.0 <1.87.1

## Details
### Impact

**Actions**, introduced in ZITADEL **1.42.0** on the API and **1.56.0** for Console, is a feature, where users with role `ORG_OWNER` are able to create Javascript Code, which is invoked by the system at certain points during the login.
**Actions**, for example, allow creating authorizations (user grants) on newly created users programmatically.
Due to a missing authorization check, **Actions** were able to grant authorizations for projects that belong to other organisations inside the same Instance. Granting authorizations via API and Console is not affected by this vulnerability.

### Patches

2.x versions are fixed on >= [2.2.0](https://github.com/zitadel/zitadel/releases/tag/v2.2.0)
1.x versions are fixed on >= [1.87.1](https://github.com/zitadel/zitadel/releases/tag/v1.87.1)

ZITADEL recommends upgrading to the latest versions available in due course.

### Workarounds

There is no workaround since a patch is already available.

### Who did disclose this

During our recurring white box penetration test our external security consultant found this issue.
The full report will be made public after the complete review.

### References

https://docs.zitadel.com/docs/guides/manage/customize/behavior
https://docs.zitadel.com/docs/apis/actions
https://zitadel.com/blog/pentest-results-h1-2021

### Questions

If you have any questions or comments about this advisory:
* Email us at [security@zitadel.com](mailto:security@zitadel.com)

## References
- https://github.com/zitadel/zitadel/security/advisories/GHSA-c8fj-4pm8-mp2c
- https://nvd.nist.gov/vuln/detail/CVE-2022-36051
- https://github.com/zitadel/zitadel/pull/4237
- https://github.com/zitadel/zitadel/pull/4238
- https://github.com/zitadel/zitadel/releases/tag/v1.87.1
- https://github.com/zitadel/zitadel/releases/tag/v2.2.0
- github.com/zitadel/zitadel
