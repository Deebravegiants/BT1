### Title
Webhook shop-domain header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signable string from the raw request body only, while the `shop` (tenant identity) is read from an unauthenticated header. `Registry.process` validates the HMAC and then dispatches to the handler using that unauthenticated `shop` value, breaking the equality `shop authenticated by HMAC == shop acted upon by the handler`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header, entirely independent of the signed bytes: [2](#0-1) 

`Utils::HmacValidator.validate` verifies the HMAC strictly against `to_signable_string` (i.e., `raw_body`), never touching `shop`, `topic`, or `webhook_id`: [3](#0-2) 

`Registry.process` accepts the request once the body's HMAC checks out, then passes the header-derived, unauthenticated `request.shop` straight to the app's webhook handler as the tenant identifier: [4](#0-3) 

Because the `api_secret_key` is a single shared secret for the whole app (not per-shop), any HMAC-valid `(raw_body, hmac)` pair obtained from a genuine webhook delivery for *any* shop under the app's install base remains HMAC-valid for *any other shop*. An attacker who controls one installed shop (an unprivileged, ordinary merchant account — no special access needed) can:
1. Trigger a real webhook to their own endpoint (e.g., by editing an order in their own store) and capture the raw body plus the `x-shopify-hmac-sha256` value Shopify sent.
2. Replay that exact `(raw_body, hmac)` pair to the app, but with the `x-shopify-shop-domain` header changed to a victim shop's domain.
3. `HmacValidator.validate` still succeeds because it only checks `raw_body` against the shared secret — it never binds the signature to the shop asserted in the headers.
4. `Registry.process` then invokes the handler with `shop: request.shop` set to the victim's domain, so the attacker-controlled `raw_body` is processed as if it came from the victim shop.

This is the resource-integrity analog called for: a field (`shop`, the tenant identity used for session/data lookups) is acted upon by the library but not covered by the HMAC that is supposed to authenticate the request.

### Impact Explanation
This crosses a tenant boundary: an unprivileged operator of Shop A can make the app process attacker-chosen payload bytes under Shop B's identity without needing Shop B's credentials, the app's `client_secret`, or any access token. Depending on how the host app's `WebhookHandler` uses `shop` (e.g., updating merchant records, revoking access on `app/uninstalled`, seeding data for `orders/create`), this enables cross-tenant data corruption or state confusion purely through this gem's own dispatch path, which meets the "cross-tenant access" criterion.

### Likelihood Explanation
Exploitability requires only: (a) attacker has (or creates) one legitimate install of the target app, which is trivial since Shopify app installation is self-serve for merchants, and (b) attacker can send an arbitrary HTTP POST to the app's public webhook endpoint with custom headers, which is standard for any internet-reachable webhook receiver. No secrets, tokens, or privileged access are required — only observation of one's own legitimately delivered webhook and header substitution on replay.

### Recommendation
Bind the shop (and ideally topic/webhook-id) into the signed material, or otherwise cryptographically tie the HMAC to the asserted tenant instead of relying solely on `raw_body`:
```diff
 sig { override.returns(String) }
 def to_signable_string
-  @raw_body
+  "#{shop}\n#{topic}\n#{@raw_body}"
 end
```
Since Shopify itself only signs the raw body over HTTP, the more robust fix is for `Registry.process` (or the host app via documentation guidance) to cross-check `request.shop` against the shop associated with a previously stored, verified session/webhook registration for that specific webhook subscription (e.g., verifying webhook_id belongs to the claimed shop) before dispatching to the handler, rather than trusting the header value implicitly once the body HMAC passes.

### Proof of Concept
```ruby
require "openssl"
require "base64"

secret = ShopifyAPI::Context.api_secret_key
raw_body = '{"id":123,"note":"legit order from shop-a"}'

# Attacker captures a genuine webhook HMAC for their own shop (shop-a.myshopify.com)
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), secret, raw_body)

# Attacker replays the same body+hmac but claims to be shop-b (a victim they don't control)
spoofed_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(hmac),
  "x-shopify-shop-domain" => "shop-b.myshopify.com", # not covered by HMAC
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: spoofed_headers)

# Passes validation despite shop-domain being forged, because only raw_body is signed
ShopifyAPI::Utils::HmacValidator.validate(request) # => true

ShopifyAPI::Webhooks::Registry.process(request)
# handler.handle is invoked with shop: "shop-b.myshopify.com" using attacker-controlled body,
# even though shop-b never sent this webhook.
```

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-200)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
        end
```
