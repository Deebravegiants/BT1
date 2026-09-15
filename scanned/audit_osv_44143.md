# [M] APITable through 1.13.0-beta.1 Missing Authentication on the Internal Account Closure Endpoints

## Summary
Severity: Medium
Advisory: CVE-2026-80208
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-80208
Type: osv

## Details
APITable through 1.13.0-beta.1 annotates both getUserHistories and closePausedUserAccount in InternalUserController with requiredLogin = false. ResourceInterceptor honours that annotation by returning before any session or API key is validated, and the nginx gateway shipped with the product proxies every /api request to the backend server, so both endpoints are reachable by any unauthenticated client that can reach the gateway. An attacker can POST to /api/v1/internal/getUserHistories to enumerate the accounts sitting in the 30-day cooling-off period that follows a deletion request, then POST to /api/v1/internal/users/{userId}/close for each one. The closure path clears the account's email address, phone number and nickname, cancels its space subscriptions, removes its space memberships and deletes its OAuth bindings, so the cooling-off window that exists to let a user reverse a deletion request is bypassed and the account cannot be recovered.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80208.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80208
- https://www.vulncheck.com/advisories/apitable-through-1.13.0-beta.1-missing-authentication-on-the-internal-account-closure-endpoints
- https://github.com/apitable/apitable/issues/1812
- https://github.com/apitable/apitable
- https://github.com/apitable/apitable/blob/88b24ce9f359cc434778be75d03603182882dc76/backend-server/application/src/main/java/com/apitable/internal/controller/InternalUserController.java#L149
