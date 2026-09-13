# [H] Vaultwarden's Collection Management Operations Allowed Without `manage` Verification for Manager Role

## Summary
Severity: High
Advisory: GHSA-h4hq-rgvh-wh27
CVE: CVE-2026-27803
CWE: CWE-269, CWE-285, CWE-863
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-03-04
Source: https://github.com/advisories/GHSA-h4hq-rgvh-wh27
Type: github-advisory

## Affected
- crates.io: `vaultwarden` — affected >=0 <1.35.4

## Details
## Summary

Testing confirmed that even when a Manager has `manage=false` for a given collection, they can still perform the following management operations as long as they have access to the collection:

* `PUT /api/organizations/<org_id>/collections/<col_id>` succeeds (HTTP 200)
* `PUT /api/organizations/<org_id>/collections/<col_id>/users` succeeds (HTTP 200)
* `DELETE /api/organizations/<org_id>/collections/<col_id>` succeeds (HTTP 200)



## Description

* The Manager guard checks only whether the user **can access the collection**, not whether they have `manage` privileges. This check is directly applied to management endpoints.
src/auth.rs:816
  ```rust

  if !Collection::can_access_collection(&headers.membership, &col_id, &conn).await {
      err_handler!("The current user isn't a manager for this collection")
  }
  ```

* The `can_access_collection` function does **not** evaluate the `manage` flag.
  src/db/models/collection.rs:140

  ```rust

  pub async fn can_access_collection(member: &Membership, col_id: &CollectionId, conn: &DbConn) -> bool {
      member.has_status(MembershipStatus::Confirmed)
          && (member.has_full_access()
              || CollectionUser::has_access_to_collection_by_user(col_id, &member.user_uuid, conn).await
              || ...
  ```

* A separate management-permission check exists and includes `manage` validation, but it is **not used** during authorization for the affected endpoints.
  src/db/models/collection.rs:516

  ```rust

  pub async fn is_manageable_by_user(&self, user_uuid: &UserId, conn: &DbConn) -> bool {
      let Some(member) = Membership::find_confirmed_by_user_and_org(user_uuid, &self.org_uuid, conn).await else {
          return false;
      };
      if member.has_full_access() {
          return true;
      }
      ...
  ```

* The actual update and deletion endpoints only accept `ManagerHeaders` and do not perform additional `manage` checks.
  src/api/core/organizations.rs:608

```rust
  async fn put_organization_collection_update(..., headers: ManagerHeaders, ...)
```

  src/api/core/organizations.rs:890

```rust
  async fn put_collection_users(..., headers: ManagerHeaders, ...)
```
  

src/api/core/organizations.rs:747

```rust
  async fn delete_organization_collection(..., headers: ManagerHeaders, ...)
  ```



## Preconditions

* The attacker is a **Manager** within the target organization.
* The attacker has access to the target collection (`assigned=true`).
* The attacker’s permission for that collection is `manage=false`.
* A valid API access token has been obtained.



## Steps to Reproduce

1. Confirm that the attacker’s current permissions for the target collection include `manage=false`.
<img width="2015" height="636" alt="image" src="https://github.com/user-attachments/assets/58ddc733-e37c-4766-a980-b1ea1918ceb4" />

2. As a control test, verify that update operations fail for collections the attacker cannot access.
<img width="2021" height="852" alt="image" src="https://github.com/user-attachments/assets/d8699442-2dfc-4d73-8940-ec10f4a175f0" />

3. Confirm that update operations succeed for the target collection where `manage=false`.
<img width="2013" height="690" alt="image" src="https://github.com/user-attachments/assets/33d9845d-d18e-456c-a58c-e780911347a9" />

4. Use `PUT /collections/{col_id}/users` to set `manage=true`, confirming that the attacker can escalate their own privileges.
<img width="2018" height="488" alt="image" src="https://github.com/user-attachments/assets/da8c5246-cf2a-46c2-9a25-e99d907f852d" />

5. Verify that deletion of the collection succeeds despite the Manager lacking management rights.
<img width="2018" height="487" alt="image" src="https://github.com/user-attachments/assets/a97c8fb2-4f97-4c2a-a90b-9d95dbde84fd" />



## Required Minimum Privileges

* Organization Manager role (Owner/Admin privileges are not required)
* Works even with `access_all=false`
* Only access rights to the target collection are required (`manage` privilege is not required)



## Attack Scenario

A restricted Manager (intended for read/use-only access) directly invokes the API to update collection settings, elevate their own privileges to `manage=true`, and even delete the collection.

This allows the user to bypass operational access restrictions and effectively gain administrator-equivalent control over the collection.



## Potential Impact

* **Confidentiality:** Expansion of access scope through unauthorized privilege escalation and configuration changes.
* **Integrity:** Unauthorized modification of collection settings and assignments; potential disabling of access controls.
* **Availability:** Deletion of collections may disrupt business operations.

## References
- https://github.com/dani-garcia/vaultwarden/security/advisories/GHSA-h4hq-rgvh-wh27
- https://github.com/dani-garcia/vaultwarden
