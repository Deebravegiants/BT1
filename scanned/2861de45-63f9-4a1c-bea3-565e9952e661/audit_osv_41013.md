# [C] CamaleonCMS 2.9.2 Privilege Escalation via Parameter Confusion in UsersController

## Summary
Severity: Critical
Advisory: CVE-2026-56721
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-56721
Type: osv

## Details
CamaleonCMS version 2.9.2 and earlier contains a privilege escalation vulnerability via insecure direct object reference (IDOR) that allows authenticated low-privileged attackers to overwrite any user's credentials by exploiting a parameter confusion flaw between the authorization filter and action body in the UsersController. Attackers can send a PATCH request to the updated_ajax endpoint setting params[:id] to their own user ID to pass the self-authorization check while simultaneously setting params[:user_id] to a victim's ID, causing the controller to load and mutate the victim's account, including overwriting administrator passwords to achieve full site takeover.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56721.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-56721
- https://www.vulncheck.com/advisories/camaleoncms-privilege-escalation-via-parameter-confusion-in-userscontroller
- https://github.com/owen2345/camaleon-cms/pull/1185
- https://github.com/owen2345/camaleon-cms/commit/26345034523a505cb01615509b7f0a665e89ae3e
- https://github.com/owen2345/camaleon-cms
