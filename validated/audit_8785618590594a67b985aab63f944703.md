Confirmed the full flow. This matches the report's bug class cleanly: an identity field (`shop`) is trusted for tenant routing but is not covered by the cryptographic proof (HMAC) that authenticates the request.

### Title
Webhook shop attribution is not covered by the HMAC, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then dispatches the parsed body to the app's handler tagged with the `shop` value taken from an unauthenticated header. Because the shop identity is never part of the signed material, any request with a body/HMAC pair that validates against the app's shared `api_secret_key` can be relabeled to any shop domain.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `shop` is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header without any cryptographic binding to that body [2](#0-1) . `Registry.process` validates the request purely via `Utils::HmacValidator.validate(request)`, which recomputes HMAC-SHA256 over `to_signable_string` (i.e., the body only) using `Context.api_secret_key`, and compares it to the `hmac` header [3](#0-2) [4](#0-3) . After that check passes, the handler is invoked with `shop: request.shop` taken straight from the header, with no cross-check that the body actually pertains to that shop [5](#0-4) .

Because `api_secret_key` is a single, app-wide secret shared across every shop that has installed the app (not a per-shop secret), the HMAC over a given body is identical regardless of which shop the payload nominally belongs to. Consequently, an attacker who has installed the target app on their own store legitimately receives real webhooks from Shopify — each with a genuinely valid `body`/`hmac` pair signed with that shared secret. The attacker can then send that exact `body`+`hmac` combination directly to the app's own webhook endpoint (bypassing Shopify's delivery entirely, since nothing prevents a client from POSTing directly to the app's public webhook route) while substituting an arbitrary `shopify-shop-domain` header value naming a different, victim shop. `HmacValidator.validate` still succeeds because the header is not part of the signed string, and `Registry.process` forwards `WebhookMetadata.new(shop: request.shop, body: request.parsed_body, ...)` to the app's handler as if the payload genuinely originated from and pertains to the victim shop [6](#0-5) .

This is the direct analog of the reported bug class: a field the application acts on for identity/tenant attribution (`shop`) is not covered by the integrity check (HMAC) that is supposed to authenticate the whole request, so the value verified (the body) and the value trusted for the security decision (the header-derived shop) diverge — `shop_verified != shop_trusted`.

### Impact Explanation
This is High severity: it enables cross-tenant data injection/confusion. Any app built on this gem that keys per-shop side effects (order records, redact/data-request handling, database writes, background jobs, notifications, GDPR compliance actions) off `WebhookMetadata#shop` can be made to attribute attacker-controlled webhook content to an arbitrary victim shop that also uses the same app, purely from data the calling application receives from this gem as "verified". No access token, `client_secret`, or privileged credential is required — only that the attacker (an ordinary internet user) has installed the app on their own store to obtain one legitimately signed body/hmac pair, and can reach the app's public webhook endpoint.

### Likelihood Explanation
Likelihood is high for any app that installs on multiple merchants (the normal SaaS app model) and exposes its webhook callback route publicly, which is the documented usage pattern in `docs/usage/webhooks.md` [7](#0-6) . Becoming an installer of the target app is trivial for an attacker (self-install on their own dev store), and webhook callback routes are, by design, unauthenticated public HTTP endpoints.

### Recommendation
Bind the shop identity into the authenticated material before it is trusted: e.g., require callers to supply/compare the shop against a value looked up from a previously-established, authenticated session/subscription record (not solely the header), or extend `to_signable_string` / a dedicated check so that the `shop-domain` header participates in the integrity verification (or is cross-validated against Shopify's known registered webhook subscription for that topic/shop) before `Registry.process` dispatches to the handler.

### Proof of Concept
1. App X is installed on Attacker's store (`attacker.myshopify.com`) and on Victim's store (`victim.myshopify.com`), both proxied through the same `Registry.process` endpoint.
2. Shopify sends Attacker a genuine webhook, e.g. `customers/data_request`, with body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)` — this pairing is valid because `api_secret_key` is shared across all shops of App X.
3. Attacker crafts a direct HTTP POST to App X's public webhook route with body `B`, header `X-Shopify-Hmac-Sha256: H` (unchanged), but `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses the forged headers/body [8](#0-7) ; `Registry.process` calls `Utils::HmacValidator.validate(request)` which succeeds because it only checks `B` against `H` [3](#0-2) .
5. The app's handler receives `WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed_body_of_B, ...)` and performs its shop-scoped side effects against Victim's tenant using Attacker-controlled payload content, even though the payload never legitimately concerned Victim.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L45-63)
```ruby
      sig { params(raw_body: String, headers: T::Hash[String, T.untyped]).void }
      def initialize(raw_body:, headers:)
        # normalize the headers by forcing lowercase, removing any prepended "http"s, and changing underscores to dashes
        headers = headers.to_h { |k, v| [k.to_s.downcase.sub("http_", "").gsub("_", "-"), v] }

        missing_headers = []
        ["topic", "hmac-sha256", "shop-domain"].each do |name|
          unless headers.key?("shopify-#{name}") || headers.key?("x-shopify-#{name}")
            missing_headers << "shopify-#{name} or x-shopify-#{name}"
          end
        end
        unless missing_headers.empty?
          raise Errors::InvalidWebhookError,
            "Missing one or more of the required HTTP headers to process webhooks: #{missing_headers}"
        end

        @headers = headers
        @raw_body = raw_body
      end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-190)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
```

**File:** lib/shopify_api/webhooks/registry.rb (L192-199)
```ruby
          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** docs/usage/webhooks.md (L123-136)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

```ruby
class WebhookController < ApplicationController
  def webhook
    ShopifyAPI::Webhooks::Registry.process(
      ShopifyAPI::Webhooks::Request.new(raw_body: request.raw_post, headers: request.headers.to_h)
    )
    render json: {success: true}.to_json
  end
end
```
```
