# [M] Vaultwarden has Unauthorized Access via Partial Update API on Another User’s Cipher

## Summary
Severity: Medium
Advisory: GHSA-w9f8-m526-h7fh
CVE: CVE-2026-27898
CWE: CWE-639
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-04
Source: https://github.com/advisories/GHSA-w9f8-m526-h7fh
Type: github-advisory

## Affected
- crates.io: `vaultwarden` — affected >=0 <1.35.4

## Details
## Summary

In the test environment, it was confirmed that an authenticated regular user can specify another user’s `cipher_id` and call:

```
PUT /api/ciphers/{id}/partial
```

Even though the standard retrieval API correctly denies access to that cipher, the partial update endpoint returns **200 OK** and exposes `cipherDetails` (including `name`, `notes`, `data`, `secureNote`, etc.).



## Description

`put_cipher_partial` retrieves the target Cipher but does **not perform ownership or access control checks** before returning `to_json`.
Authorization checks present in the normal update API are missing here.
src/api/core/ciphers.rs:717

```rust
let Some(cipher) = Cipher::find_by_uuid(&cipher_id, &conn).await else {
    err!("Cipher doesn't exist")
};

if let Some(ref folder_id) = data.folder_id {
    if Folder::find_by_uuid_and_user(folder_id, &headers.user.uuid, &conn).await.is_none() {
        err!("Invalid folder", "Folder does not exist or belongs to another user");
    }
}

// Move cipher
cipher.move_to_folder(data.folder_id.clone(), &headers.user.uuid, &conn).await?;

// Update favorite
cipher.set_favorite(Some(data.favorite), &headers.user.uuid, &conn).await?;

Ok(Json(cipher.to_json(&headers.host, &headers.user.uuid, None, CipherSyncType::User, &conn).await?))
```

By comparison, the standard update API includes an explicit authorization check:
src/api/core/ciphers.rs:688

```rust
if !cipher.is_write_accessible_to_user(&headers.user.uuid, &conn).await {
    err!("Cipher is not write accessible")
}
```

The `to_json` method does not abort processing when access restrictions are not met; instead, it proceeds to construct and return a detailed response.
src/db/models/cipher.rs:175

```rust
let (read_only, hide_passwords, _) = if sync_type == CipherSyncType::User {
    match self.get_access_restrictions(user_uuid, cipher_sync_data, conn).await {
        Some((ro, hp, mn)) => (ro, hp, mn),
        None => {
            error!("Cipher ownership assertion failure");
            (true, true, false)
        }
    }
} else {
    (false, false, false)
};
```
src/db/models/cipher.rs:335

```rust
let mut json_object = json!({
    "object": "cipherDetails",
    "id": self.uuid,
    "type": self.atype,
    ...
    "name": self.name,
    "notes": self.notes,
    "fields": fields_json,
    "data": data_json,
    ...
});
```


## Preconditions

* The attacker possesses a valid regular-user JWT (Bearer token).
* The attacker knows the target (victim) `cipher_id`.


## Steps to Reproduce

1. Prepare the attacker JWT and victim `cipher_id` (preconditions).
2. Baseline check: confirm that standard retrieval is denied.
<img width="2014" height="855" alt="image" src="https://github.com/user-attachments/assets/32b12cc9-3672-4a88-afd0-ef7715474662" />


3. Execute the vulnerable API. Confirm that **200 OK** is returned and that `cipherDetails` includes fields such as `id`, `name`, `notes`, `secureNote`, etc.
<img width="2018" height="1113" alt="image" src="https://github.com/user-attachments/assets/341b330c-8d55-4f06-a622-0d7da28f62fd" />


## Potential Impact

* Unauthorized disclosure of other users’ cipher information (confidentiality breach).
* Creation of unauthorized associations within the attacker’s user context (e.g., `favorite` or folder operations).
* The response from `/api/ciphers/<cipher_id>/partial` includes `attachments[].url`.

In filesystem (FS) deployments, this returns a tokenized endpoint such as:

```
/attachments/<cipher>/<file>?token=...
```

In object storage deployments, it returns a short-lived pre-signed URL.

As a result, an attacker can use these URLs to directly download attachment data that they are not authorized to access.

This can lead to disclosure of sensitive information stored in the Vault, including personal data and authentication credentials. Such exposure may further result in account compromise, lateral movement, and other secondary impacts.

## References
- https://github.com/dani-garcia/vaultwarden/security/advisories/GHSA-w9f8-m526-h7fh
- https://github.com/dani-garcia/vaultwarden
