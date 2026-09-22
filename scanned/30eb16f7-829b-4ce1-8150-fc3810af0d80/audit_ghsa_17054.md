# [M] Kimai API returns timesheet entries a user should not be authorized to view

## Summary
Severity: Medium
Advisory: GHSA-cj3c-5xpm-cx94
CVE: CVE-2024-29200
CWE: CWE-1220
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2024-03-29
Source: https://github.com/advisories/GHSA-cj3c-5xpm-cx94
Type: github-advisory

## Affected
- Packagist: `kimai/kimai` — affected >=0 <2.13.0

## Details
### Summary
The permission `view_other_timesheet` performs differently for the Kimai UI and the API, thus returning unexpected data through the API.

### Details
When setting the `view_other_timesheet` permission to true, on the frontend, users can only see timesheet entries for teams they are a part of. When requesting all timesheets from the API, however, all timesheet entries are returned, regardless of whether the user shares team permissions or not.

Example:
There are projects P1 and P2, Teams T1 and T2, users U1 and U2 and Timesheet entries E1 and E2. U1 is team leader of team T1 and has access to P1. U2 is in Team T2 and has access to both P1 and P2. U2 creates E1 for P1 and E2 for P2.
In the UI, U1 with `view _other_timesheet` perms sees E1 as he is a part of T1 that has access to P1.
In the API, however, he has access to E1 **and E2**.

Additionally, if U1 is not a team leader T1, he does not see any timesheet from a user other than himself in the UI, but still all timesheets in the API.

### PoC
- Give a user `view_other_timesheet` permission
- The result of the UI and the API call to `/api/timesheets?user=all` differs in the data that is being returned

Curl command:
```bash
curl -X 'GET' \
  'https://kimai.instance.com/api/timesheets?user=all' \
  -H 'accept: application/json' \
  -H 'X-AUTH-USER: username' \
  -H 'X-AUTH-TOKEN: api_token'
 ```

### Impact
This is at least an insufficient granularity of access control weakness. People can see timesheet entries they are not supposed to.
This greatly affects the confidentiality of timesheet entries. 

Restricting API access to administrators is also not a valid solution, as API access is needed, for example, to use the mobile app.

## References
- https://github.com/kimai/kimai/security/advisories/GHSA-cj3c-5xpm-cx94
- https://nvd.nist.gov/vuln/detail/CVE-2024-29200
- https://github.com/kimai/kimai
- https://github.com/kimai/kimai/releases/tag/2.13.0
