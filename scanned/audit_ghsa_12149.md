# [H] Vaultwarden has Privilege Escalation via Bulk Permission Update to Unauthorized Collections by Manager

## Summary
Severity: High
Advisory: GHSA-r32r-j5jq-3w4m
CVE: CVE-2026-27802
CWE: CWE-269, CWE-863
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-03-04
Source: https://github.com/advisories/GHSA-r32r-j5jq-3w4m
Type: github-advisory

## Affected
- crates.io: `vaultwarden` — affected >=0 <1.35.4

## Details
## Summary

A Manager account (`access_all=false`) was able to escalate privileges by directly invoking the **bulk-access API** against collections that were not originally assigned to them.
The API allowed changing `assigned=false` to `assigned=true`, resulting in unauthorized access.

Additionally, prior to the bulk-access call, the regular single-update API correctly returned **401 Unauthorized** for the same collection. After executing the bulk-access API, the same update API returned **200 OK**, confirming an authorization gap at the HTTP level.

---

## Description

* The endpoint accepts `ManagerHeadersLoose` and does not validate access rights for the specified `collectionIds`.
  src/api/core/organizations.rs:551

  ```rust
  headers: ManagerHeadersLoose,
  ```

* The received `collection_ids` are processed directly without per-collection authorization checks.
  src/api/core/organizations.rs:564

  ```rust
  for col_id in data.collection_ids {
  ```

* Existing group assignments for the collection are deleted.
  src/api/core/organizations.rs:583

  ```rust
  CollectionGroup::delete_all_by_collection(&col_id, &conn).await?;
  ```

* Existing user assignments for the collection are deleted.
  src/api/core/organizations.rs:590

  ```rust
  CollectionUser::delete_all_by_collection(&col_id, &conn).await?;
  ```

* By comparison, another bulk-processing endpoint performs per-collection validation using `from_loose`.
  src/api/core/organizations.rs:787

  ```rust
  let headers = ManagerHeaders::from_loose(headers, &collections, &conn).await?;
  ```

* The actual access control logic is implemented in `can_access_collection`, which is not invoked in the bulk-access endpoint.
  src/auth.rs:911

  ```rust
  if !Collection::can_access_collection(&h.membership, col_id, conn).await {
  ```

---

## Preconditions

* The attacker possesses a valid **Manager account** within the target organization.
* The organization contains collections that are **not assigned** to the attacker.
* The attacker can authenticate through the standard API login process (Owner/Admin privileges are not required).

---

## Steps to Reproduce

1. Log in as a Manager and obtain a Bearer token.
<img width="4016" height="1690" alt="image" src="https://github.com/user-attachments/assets/218f05e2-6a2e-4066-8f8d-6bbef1cc5858" />

2. Confirm the current values of `assigned`, `manage`, `readOnly`, and `hidePasswords` for the target collection.
<img width="4026" height="1694" alt="image" src="https://github.com/user-attachments/assets/a6d2fc70-5370-4984-85bd-a6f74febdfa3" />

3. Verify that the standard update API returns **401 Unauthorized** when attempting to modify the unassigned collection.
<img width="4030" height="1708" alt="image" src="https://github.com/user-attachments/assets/802f0d2b-d474-44d2-beef-b4f7f3335225" />

4. Invoke the bulk-access API, including:
<img width="4036" height="1120" alt="image" src="https://github.com/user-attachments/assets/1d3caa01-3ac2-4636-9ed0-189e5923c986" />

   * `collectionIds` containing the target collection
   * `users` containing the attacker’s own `membership_id`
     Confirm that the API returns **200 OK**.

5. Re-run the standard update API.
   Confirm that it now succeeds and that the previously unauthorized modification is applied.
<img width="4040" height="1440" alt="image" src="https://github.com/user-attachments/assets/340e9676-d802-404c-b894-9986a176360a" />

---

## Required Minimum Privileges

* Manager role within the target organization
  (the issue occurs even when `access_all=false`)

---

## Attack Scenario

A delegated administrator or department-level Manager within an organization directly calls the API to add themselves to unauthorized collections and gain access to confidential information.

Because the bulk update process deletes and reassigns existing permissions, the attacker can also remove other users’ access, enabling denial-of-service or sabotage within the organization.

---

## Potential Impact

* **Confidentiality:** Unauthorized access to sensitive information within restricted collections.
* **Integrity:** Unauthorized modification of collection permission settings and arbitrary changes to access controls.
* **Availability:** Deletion of existing assignments may cause legitimate users to lose access.

## References
- https://github.com/dani-garcia/vaultwarden/security/advisories/GHSA-r32r-j5jq-3w4m
- https://github.com/dani-garcia/vaultwarden
