# [H] AVideo: OS command injection in on_publish.php execAsync via unescaped m3u8 URL

## Summary
Severity: High
Advisory: GHSA-xw67-cg5f-4m2r
CVE: CVE-2026-45578
CWE: CWE-78
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-15
Source: https://github.com/advisories/GHSA-xw67-cg5f-4m2r
Type: github-advisory

## Affected
- Packagist: `WWBN/AVideo` — affected >=0

## Details
## Summary

**Type:** Classic shell-metacharacter injection. The YPTSocket notification branch in `plugin/Live/on_publish.php` builds an `execAsync()` command line by string concatenation, single-quoting each argument but never calling `escapeshellarg()`. A `'` in any of the three interpolated values (`$users_id`, `$m3u8`, `$obj->liveTransmitionHistory_id`) closes the quoted token and lets the attacker append arbitrary commands.
**File:** `plugin/Live/on_publish.php`, line 267.
**Root cause:** the developer wrapped each variable in literal single quotes (`'$users_id'`, `'$m3u8'`, `'$obj->liveTransmitionHistory_id'`) believing this provides shell-quoting. PHP single-quoted-into-shell is not safe quoting; it is just two literal quote characters that the shell pairs greedily. Any embedded `'` closes the outer string and resumes interpretation in the shell. The rest of the AVideo codebase already calls `escapeshellarg()` (137 call sites across the project) for ffmpeg invocations, so the safe primitive is well-known to the project; it was simply omitted from this branch. The endpoint is web-reachable (no `.htaccess` rule restricts `on_publish.php`, no `REMOTE_ADDR` check), so the trigger is a direct HTTP POST without going through nginx-rtmp.

## Affected Code

**File:** `plugin/Live/on_publish.php`, lines 256-271.

```php
if (AVideoPlugin::isEnabledByName('YPTSocket')) {
    $array = setLiveKey($lth->getKey(), $lth->getLive_servers_id());
    @ob_clean();
    _ob_start();
    $lth = new LiveTransmitionHistory($obj->liveTransmitionHistory_id);
    $m3u8 = Live::getM3U8File($lth->getKey(), false, true);          // value-carrying URL: contains the stream key verbatim
    $users_id = $obj->row['users_id'];
    $liveTransmitionHistory_id = $obj->liveTransmitionHistory_id;
    if (strtoupper(substr(PHP_OS, 0, 3)) === 'WIN') {
        include "{$global['systemRootPath']}plugin/Live/on_publish_socket_notification.php";
    } else {
        $command = get_php(). " {$global['systemRootPath']}plugin/Live/on_publish_socket_notification.php '$users_id' '$m3u8' '{$obj->liveTransmitionHistory_id}'";  // <-- BUG: literal quotes, no escapeshellarg
        $pid = execAsync($command);                                  // sink: shell exec
    }
}
```

`Live::getM3U8File($key, false, true)` (`Live.php:1337-1350` -> `Live.php:4845-4889`) returns `"{$playerServer}{$uuid}.m3u8"` (or `"{$playerServer}{$uuid}/index.m3u8"`) where `$uuid = $this->getKeyWithIndex(...)` is the stream key string read straight out of the `live_transmitions` table. There is no character normalisation between database read and command construction.

**Why it's wrong:** `'$m3u8'` is not shell quoting. PHP interpolates `$m3u8` into the string between two literal `'` characters. The shell then tokenises the result. If `$m3u8` contains `'` itself, the shell sees `'…'` followed by `<attacker bytes>` followed by another `'`, which forms two adjacent quoted strings concatenated with whatever the attacker put between them. Embedded `;`, backticks, `$()`, `&&`, `|`, or `\n` then run as shell commands. The fix is `escapeshellarg()`, which AVideo already uses 137 times in ffmpeg invocations (e.g. `getVideos.php:1069`, `videos.json.php`, `aVideoEncoder.json.php`); this branch simply forgot it.

## Exploit Chain

1. Attacker authenticates and arranges for one of the command variables to contain `'`. Under the current code the readily available primitive is a `canStream` user supplying a stream key via the persistence path (`saveLive.php`'s `$_REQUEST['key']` is written verbatim to `live_transmitions.key`). State: a row exists with `key = "evilkey';id>/tmp/pwn;#"`.
2. Attacker POSTs directly to `https://target/plugin/Live/on_publish.php` (the file is web-served, no IP restriction) with body:
   ```
   name=evilkey';id>/tmp/pwn;#
   p=<md5(attacker_password)>
   tcurl=rtmp://target/live
   addr=1.2.3.4
   ```
   `on_publish.php:117` runs `preg_replace("/[&=]/", '', $_POST['name'])` — only `&`/`=` are stripped, so `';id>/tmp/pwn;#` survives. Lines 143-163 confirm `$_GET['p'] === $user->getPassword()` (the attacker is themself, knows their own MD5), persist a `LiveTransmitionHistory` row with the poisoned key, and set `$obj->error = false`. State: authorisation gate passed.
3. Line 261 calls `Live::getM3U8File($lth->getKey(), false, true)`, returning `"https://server/live/evilkey';id>/tmp/pwn;#.m3u8"`. State: `$m3u8` carries the injection payload.
4. Line 267 builds the command string by concatenation:
   ```
   php /var/www/AVideo/plugin/Live/on_publish_socket_notification.php '7' 'https://server/live/evilkey';id>/tmp/pwn;#.m3u8' '42'
   ```
   Shell tokenisation sees: `php`, `…/on_publish_socket_notification.php`, `'7'`, `'https://server/live/evilkey'` (the attacker's `'` closed the second quote), then operator `;`, then command-2 `id>/tmp/pwn`, then `;`, then `#.m3u8' '42'` (everything after `#` is a comment). State: the shell has parsed two real commands.
5. Line 269 `execAsync($command)` spawns the shell, which runs the secondary command `id>/tmp/pwn` as the AVideo PHP-FPM/Apache user. State: arbitrary OS command execution with the privileges of the web-server runtime user.
6. Final state: the attacker reads `/tmp/pwn`, swaps the payload for a reverse shell, exfiltrates `videos/configuration.php` (database password and root URL), drops a webshell into the upload tree, or pivots to other plugin credentials (PayPal/Stripe API keys, AWS keys for the CDN plugin, OpenAI key for the AI plugin).

## Security Impact

**Severity:** sec-high. Pre-auth-friendly remote code execution: the only prerequisite is that the attacker can place a `'` into one of the three command-line variables, which on a streaming platform means a single low-privilege account.
**Attacker capability:** with one `canStream` account and two HTTP requests, the attacker executes arbitrary shell commands as the AVideo runtime user. From there: read database credentials, exfiltrate user data, write a webshell into a publicly-served path, pivot to plugin credentials, persist via cron, or escalate via any local sudoers entries.
**Preconditions:** AVideo deployment with `Live` and `YPTSocket` plugins enabled (the standard live-streaming bundle); attacker can reach `/plugin/Live/on_publish.php` over the network; a value containing `'` is reachable into `users_id`, `m3u8`, or `liveTransmitionHistory_id` (the current code lets `canStream` users supply such a value via the stream-key persistence path).
**Differential:** source-inspection-verified end-to-end. The shell-tokenising behaviour of `'…'…'…'` is reproducible offline:

```sh
$ s="php /a/b.php '7' 'https://s/live/evilkey';id>/tmp/pwn;#.m3u8' '42'"
$ rm -f /tmp/pwn; bash -c "$s" 2>/dev/null; ls -l /tmp/pwn
-rw-r--r-- 1 user user N <date> /tmp/pwn        # injected `id` ran, output captured
```

The patched build (with the suggested `escapeshellarg()` fix below applied) constructs `php /a/b.php '7' 'https://s/live/evilkey'\''id>/tmp/pwn;#.m3u8' '42'`, which the shell parses as a single argument containing the literal characters; the second command never runs.

## Suggested Fix

Use `escapeshellarg()` on every variable interpolated into the command string. This matches established project conventions (137 other call sites for ffmpeg invocations).

```diff
--- a/plugin/Live/on_publish.php
+++ b/plugin/Live/on_publish.php
@@ -264,7 +264,11 @@
         if (strtoupper(substr(PHP_OS, 0, 3)) === 'WIN') {
             include "{$global['systemRootPath']}plugin/Live/on_publish_socket_notification.php";
         } else {
-            $command = get_php(). " {$global['systemRootPath']}plugin/Live/on_publish_socket_notification.php '$users_id' '$m3u8' '{$obj->liveTransmitionHistory_id}'";
+            $command = get_php()
+                . ' ' . escapeshellarg($global['systemRootPath'] . 'plugin/Live/on_publish_socket_notification.php')
+                . ' ' . escapeshellarg((string) $users_id)
+                . ' ' . escapeshellarg((string) $m3u8)
+                . ' ' . escapeshellarg((string) $obj->liveTransmitionHistory_id);
             _error_log("NGINX Live::on_publish YPTSocket start  ($command)");
             $pid = execAsync($command);
         }
```

Defence-in-depth: `on_publish.php` is the nginx-rtmp webhook and should not be reachable from the public Internet. Add an `.htaccess`/nginx `location` rule restricting the file to `127.0.0.1` and any configured RTMP server IPs. That blocks the trigger path independently of the sanitisation work.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-xw67-cg5f-4m2r
- https://nvd.nist.gov/vuln/detail/CVE-2026-45578
- https://github.com/WWBN/AVideo
