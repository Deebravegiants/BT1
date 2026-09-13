# [H] OpenRemote has Improper Access Control via updateUserRealmRoles function

## Summary
Severity: High
Advisory: GHSA-49vv-25qx-mg44
CVE: CVE-2026-41166
CWE: CWE-284
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-49vv-25qx-mg44
Type: github-advisory

## Affected
- Maven: `io.openremote:openremote-manager` — affected >=0 <1.22.1

## Details
### Summary
A user who has `write:admin` in one Keycloak realm can call the Manager API to update **Keycloak realm roles** for users in **another** realm, including **`master`**. The handler uses the `{realm}` path segment when talking to the identity provider but does not check that the caller may administer that realm. This could result in a privilege escalation to `master` realm administrator if the attacker controls any user in `master` realm.

### Details
In `manager/src/main/java/org/openremote/manager/security/UserResourceImpl.java`, there is no check to validate if the caller should be able to administer a realm they're trying to update.

```340:353:manager/src/main/java/org/openremote/manager/security/UserResourceImpl.java
    @Override
    public void updateUserRealmRoles(RequestParams requestParams, String realm, String userId, String[] roles) {
        try {
            identityService.getIdentityProvider().updateUserRealmRoles(
                realm,
                userId,
                roles);
        } catch (ClientErrorException ex) {
            ex.printStackTrace(System.out);
            throw new WebApplicationException(ex.getCause(), ex.getResponse().getStatus());
        } catch (Exception ex) {
            throw new WebApplicationException(ex);
        }
    }
```

### PoC
1. Create a **new** Keycloak realm other than `master`. Add a user and grant that user the OpenRemote client role `write:admin`. Remember the realm name (call it `NEW_REALM`).
2. In Keycloak realm `master`, pick a **low-privilege** user (no `admin` realm role). Copy that user’s UUID (`<master-user-uuid>`).
3. Authenticate as the user from step 1 and obtain a Bearer access token (`<token>`) for `NEW_REALM`.
4. Replace placeholders and run:
```bash
curl -k -X PUT "https://<host>/api/<NEW_REALM>/user/master/userRealmRoles/<master-user-uuid>" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '["admin"]'
```
5. In the Keycloak Admin Console, realm master, that user, Role mapping. Confirm the admin realm role is assigned.
### Impact
An attacker with the OpenRemote client role write:admin in any realm can call this API with {realm} set to another realm (for example master) and change Keycloak realm roles for users there. That can grant admin on master to a user UUID they target, which gives Keycloak administrator access for the master realm.

## References
- https://github.com/openremote/openremote/security/advisories/GHSA-49vv-25qx-mg44
- https://nvd.nist.gov/vuln/detail/CVE-2026-41166
- https://github.com/openremote/openremote
- https://github.com/openremote/openremote/releases/tag/1.22.1
