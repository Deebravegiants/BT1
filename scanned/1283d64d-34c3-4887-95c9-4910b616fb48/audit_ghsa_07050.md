# [H] OAuth: Cross-origin token-request redirects can expose signed request metadata

## Summary
Severity: High
Advisory: GHSA-prq8-7wvh-44qh
CVE: CVE-2026-54605
CWE: CWE-200, CWE-346, CWE-918
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-07-28
Source: https://github.com/advisories/GHSA-prq8-7wvh-44qh
Type: github-advisory

## Affected
- RubyGems: `oauth` — affected >=0.5.5 <1.1.6

## Details
# Cross-origin OAuth token-request redirects can expose signed request metadata

## Summary

When an application uses `OAuth::Consumer` to request OAuth 1.0 request tokens or
access tokens, the token request helper follows `300..399` redirects returned by
the OAuth server. In affected versions, `OAuth::Consumer#token_request` parses the
raw `Location` header, follows the redirect recursively, and can mutate the
consumer's configured `site` when the redirect points to a different host with
the same path.

The result is a cross-origin signed-request disclosure primitive: if an OAuth
server token endpoint returns a redirect whose target an attacker controls, the
client can re-sign the token request and send OAuth 1.0 request metadata,
including the OAuth signature, nonce, timestamp, consumer key, and any request
parameters included in the signature base string, to the attacker-controlled
host. The same behavior can also be used as an SSRF or confused-deputy primitive
because the application server follows the redirect and sends the next request
from its own network position.

## Affected

- `oauth` v1.1.5 and prior versions back to and including v0.5.5.
  - The cross-host token redirect behavior was introduced by
    https://github.com/ruby-oauth/oauth/commit/d74b767f
  - The behavior is documented in the v0.5.5 changelog as "Allow redirect to
    different host but same path".
- The vulnerable behavior is in `OAuth::Consumer#token_request`, which is used by
  the documented request-token and access-token flows.
- The issue is not specific to a Ruby engine or platform. It is caused by the
  gem's redirect handling and recursive token request behavior.

Patched version: `oauth` v1.1.6.

## Impact

A consumer that calls `OAuth::Consumer#get_request_token`,
`OAuth::Consumer#get_access_token`, or lower-level token request helpers against
an OAuth server whose token endpoint redirect target can be influenced may lose
three security properties:

1. **Cross-origin signed-request metadata disclosure.** The redirected request is
   signed for the attacker-controlled endpoint. Depending on the request method,
   scheme, and parameters, the attacker may receive OAuth 1.0 parameters such as
   `oauth_consumer_key`, `oauth_signature_method`, `oauth_timestamp`,
   `oauth_nonce`, `oauth_version`, and `oauth_signature`.
2. **SSRF from the application server.** The OAuth client follows the redirect on
   behalf of the application, so the redirected host is contacted from the
   application server's network position.
3. **Confused-deputy behavior.** A malicious or compromised token endpoint can
   cause an otherwise trusted application to initiate signed requests to an
   unintended origin.

The disclosed OAuth 1 signature is not equivalent to an OAuth 2 bearer token: it
is bound to the signed request, timestamp, nonce, HTTP method, and request URL.
However, it can still disclose sensitive integration metadata, may be replayable
within the receiver's accepted nonce/timestamp window in some deployments, and
can expose application-server reachability to attacker-selected hosts.

## Vulnerable code

[`lib/oauth/consumer.rb`](https://github.com/ruby-oauth/oauth/blob/v1.1.5/lib/oauth/consumer.rb)
at tag `v1.1.5`:

```ruby
def token_request(http_method, path, token = nil, request_options = {}, *arguments)
  request_options[:token_request] ||= true
  response = request(http_method, path, token, request_options, *arguments)
  case response.code.to_i

  when (200..299)
    # parse token response
  when (300..399)
    # Parse redirect to follow
    uri = URI.parse(response["location"])
    our_uri = URI.parse(site)

    # Guard against infinite redirects
    response.error! if uri.path == path && our_uri.host == uri.host

    if uri.path == path && our_uri.host != uri.host
      options[:site] = "#{uri.scheme}://#{uri.host}"
      @http = create_http
    end

    token_request(http_method, uri.path, token, request_options, arguments)
  when (400..499)
    raise OAuth::Unauthorized, response
  else
    response.error!
  end
end
```

The vulnerable behavior has several parts:

- `response["location"]` is trusted as the next token request target.
- Redirects are followed for every `300..399` response.
- There is no general redirect counter or maximum redirect limit.
- Cross-host redirects with the same path can mutate `options[:site]` and rebuild
  the underlying HTTP client.
- The recursive call continues the token request flow and signs the next request
  for the redirected destination.

## Reachable in production

The vulnerable path is reachable through the normal OAuth 1 token exchange:

```ruby
consumer = OAuth::Consumer.new(
  consumer_key,
  consumer_secret,
  site: "https://provider.example"
)

request_token = consumer.get_request_token
```

If `https://provider.example/oauth/request_token` returns a redirect to an
attacker-controlled host, the library follows that redirect as part of the token
request flow. A realistic trigger is an OAuth provider, gateway, or reverse proxy
that emits `Location` based on user-controlled or tenant-controlled input, or a
malicious tenant-controlled OAuth endpoint in a multi-tenant integration.

No application-level redirect handling is required. The redirect is followed
inside the gem before the application receives the token response.

## Reproduction

A vulnerable application is one that uses `OAuth::Consumer` to perform an OAuth
1 token exchange against a token endpoint that can be made to return a redirect
to another origin.

Example shape:

```ruby
consumer = OAuth::Consumer.new(
  consumer_key,
  consumer_secret,
  site: "https://provider.example"
)

consumer.get_request_token
```

If `https://provider.example/oauth/request_token` responds with a `30x` redirect
whose `Location` points to `https://attacker.example/...`, affected versions may
follow that redirect as part of the token request flow. The redirected request is
then generated and signed by the application server for the new destination.
Depending on the configured OAuth request scheme, OAuth 1 parameters may be sent
in the `Authorization` header, request body, or query string.

Expected vulnerable behavior:

- the token request leaves the configured OAuth provider origin;
- the redirected host receives a signed OAuth 1 token request;
- the application does not get a chance to inspect or approve the redirect target
  before the redirected request is sent.

Expected patched behavior:

- same-origin redirects continue to work, subject to a redirect limit;
- cross-origin token endpoint redirects are rejected by default;
- applications that intentionally require cross-origin token redirects must opt
  in explicitly with `token_request_cross_origin_redirects`.

## Suggested fix

Reject cross-origin token endpoint redirects by default and require explicit
opt-in for integrations that intentionally depend on that behavior.

The fix released in v1.1.6 does the following:

```ruby
current_uri = token_request_uri(path)
redirected_uri = token_request_redirect_uri(current_uri, response)
response.error! unless redirected_uri

redirect_count = request_options[:token_request_redirect_count].to_i + 1
response.error! if redirect_count > token_request_max_redirects(request_options)
response.error! if token_request_cross_origin?(current_uri, redirected_uri) &&
  !token_request_cross_origin_redirects?(request_options)

redirect_options = request_options.merge(token_request_redirect_count: redirect_count)
token_request(http_method, token_request_redirect_path(current_uri, redirected_uri), token, redirect_options, *arguments, &block)
```

The fix intentionally preserves same-origin redirect compatibility while making
cross-origin token endpoint redirects an explicit choice. It also avoids placing
internal redirect state in `request_options` passed to OAuth signing.

## Workarounds

Until a patched release is available, applications can reduce exposure by doing
one or more of the following:

- Ensure configured OAuth token endpoints are fixed absolute URLs controlled by a
  trusted provider.
- Do not use tenant-controlled OAuth token endpoint URLs unless the tenant is
  trusted to receive signed OAuth token requests.
- Block outbound application-server traffic to internal metadata services and
  other sensitive internal addresses at the network layer.
- Place a trusted proxy in front of OAuth providers that rejects token endpoint
  redirects to a different origin.

These mitigations reduce exploitability but do not remove the vulnerable redirect
logic from the gem.

## Credit

Found during the follow-up audit for `GHSA-pp92-crg2-gfv9`.

Reporter/coordinator: Peter H. Boling (`pboling`).

## References

- Related OAuth 2 advisory: https://github.com/ruby-oauth/oauth2/security/advisories/GHSA-pp92-crg2-gfv9
- Fixed version: `oauth` v1.1.6
- Behavior-introducing commit: https://github.com/ruby-oauth/oauth/commit/d74b767f

## References
- https://github.com/ruby-oauth/oauth/security/advisories/GHSA-prq8-7wvh-44qh
- https://github.com/ruby-oauth/oauth/commit/d069dc8c4c9631947451215f07460d6cdf0caf3f
- https://github.com/ruby-oauth/oauth
- https://github.com/ruby-oauth/oauth/releases/tag/v1.1.6
