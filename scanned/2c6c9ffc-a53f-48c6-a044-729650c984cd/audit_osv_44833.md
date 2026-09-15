# [M] snipe-it before 8.7.0 Authorization Bypass via API User Create/Update

## Summary
Severity: Medium
Advisory: CVE-2026-86750
Aliases: GHSA-c929-qxg6-r3mc
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:H/SA:N)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-86750
Type: osv

## Details
Snipe-IT versions <= 8.6.3 (fixed in 8.7.0) do not validate company assignment authorization before persisting user records via the REST API. In Api\UsersController::store() and ::update(), the user record is filled from the request and saved before the requested company_id / company_ids[] values are filtered against the actor's permitted companies (Company::getIdsForCurrentUser()). On installs using Full Multiple Companies Support (FMCS), a non-superuser holding users.create (or users.edit on a target user) can submit company identifiers for companies outside their scope — including a mix of permitted and foreign ids — causing the account row to be committed to the database before authorization is checked. Where null_company_is_floater=1 is set, the post-hoc filter leaves an empty company pivot and the account is persisted as a "floater" with cross-company visibility, allowing creation or relocation of user accounts across tenant boundaries.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86750.json
- https://github.com/grokability/snipe-it/security/advisories/GHSA-c929-qxg6-r3mc
- https://nvd.nist.gov/vuln/detail/CVE-2026-86750
- https://www.vulncheck.com/advisories/snipe-it-before-8.7.0-authorization-bypass-via-api-user-create-update
