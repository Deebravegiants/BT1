# [C] EGroupware has a Remote Code Execution Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-h9qx-v5xp-ph8p
CVE: CVE-2026-27823
CWE: CWE-22, CWE-639, CWE-94
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-07
Source: https://github.com/advisories/GHSA-h9qx-v5xp-ph8p
Type: github-advisory

## Affected
- Packagist: `egroupware/egroupware` — affected >=26.0.20251208 <26.2.20260224
- Packagist: `egroupware/egroupware` — affected >=0 <23.1.20260224

## Details
## Summary
A critical vulnerability has been identified in EGroupware that may lead to Remote Code Execution (RCE).
The issue allows an authenticated attacker to execute arbitrary commands on the server. If user self-registration is enabled, the vulnerability may be exploitable without prior authentication.

The vulnerability stems from improper authorization checks combined with a file write primitive and an arbitrary file read vulnerability, which together enable full system compromise.

## Details
### 1. Improper Authorization in SmallPartMediaRecorder::ajax_upload()

The vulnerability originates in:

`EGroupware\SmallParT\Widgets\SmallPartMediaRecorder::ajax_upload()`

The function attempts to verify whether the current user is a teacher of the specified course ID before allowing a file upload.

The critical authorization check ensures that the course access control list (ACL) contains:

`$required_acl (self::ROLE_TEACHER, i.e., 3)`

However, the `course_acl `value is derived from user-controlled request data.

**_Bypass Technique_**

A crafted request can manipulate the `participant_role `value inside the request body:

```json
{
  "video": {
    "course_id": {
      "participants": [
        {
          "account_id": "7",
          "name": "Test",
          "joined_at": "2026-01-10",
          "participant_role": 3
        }
      ],
      "account_id": "7",
      "course_id": "1"
    },
    "video_hash": ".",
    "video_type": "file_here"
  }
}
```

Because the course ACL is taken from `participant_role`, setting it to 3 allows bypassing the `isTeacher `check.

### 2. Arbitrary File Write

After bypassing authorization, the function uploads the provided file into a controllable file path.

The file path is derived from the `video_type `(or video_path) value, enabling path traversal.

Due to file permission restrictions (server running as www-data), writable targets are limited. One viable target is `./header.inc.php`

### 3. Constraints

Writing a simple PHP webshell may not immediately execute due to OPcache.

An invalid `header.inc.php` file will break the system and prevent the server from running.

Therefore, a valid file structure must be preserved.

### 4. Arbitrary File Read

A second vulnerability allows arbitrary file read via:

`/egroupware/index.php?menuaction=importexport.importexport_export_ui.download&_filename=../../../usr/share/egroupware/header.inc.php&_suffix=txt&_type=text/plain&filename=leak`

The issue resides in:

`importexport_export_ui::download`

The `_filename `parameter is user-controlled and used to read arbitrary files.

This allows retrieving the original `header.inc.php` content.

### 5. Achieving Remote Code Execution

By combining: Arbitrary file read (to retrieve valid header.inc.php); Arbitrary file write (to overwrite it with modified content), an attacker can inject controlled PHP code while preserving file validity.

This results in Remote Code Execution after server restart, or OPcache expiration. An alternative impact includes modifying the admin setup password to gain full system control.

## Impact
Remote Code Execution
Full system compromise
Arbitrary file read
Arbitrary file write
Potential complete takeover of EGroupware instance

## Reported by
This finding was discovered by Huong Kieu of Cenobe Security (https://cenobe.com/)

## References
- https://github.com/EGroupware/egroupware/security/advisories/GHSA-h9qx-v5xp-ph8p
- https://github.com/EGroupware/egroupware
