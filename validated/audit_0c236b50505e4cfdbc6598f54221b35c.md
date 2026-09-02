Confirmed: `Registry.process` (lib/shopify_api/webhooks/registry.rb:188-200) validates the webhook solely via `HmacValidator.validate(request)`, whose signable string is `request.to_signable_string` (lib/shopify_api/webhooks/request.rb:35-38), which returns only `@raw_body`. The `shop` value (line 21-23) comes from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is **not part of the signed material at all**. The webhook secret used is the app-wide `Context.api_secret_key` (lib/shopify_api/utils/hmac_validator.rb:16), identical across every shop that installs the app — it is not shop-specific. This means any raw body + valid HMAC pair recorded from one authenticated shop can be replayed with an attacker-supplied `shop-domain` header claiming to be a different shop, and `Registry.process` will pass it straight to the host app's handler as `WebhookMetadata` (registry.rb:198-199) with that spoofed `shop` value, without ever checking that the header-derived shop is consistent with anything the HMAC actually covers.

### Title
Webhook shop identity is unauthenticated: HMAC covers only the raw body, allowing tenant impersonation via the `shop-domain` header - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` signs only the raw request body. The `shop` attribute that the gem hands to application webhook handlers is read from a separate, unsigned HTTP header. Because Shopify webhooks are signed with the app's single `client_secret` (identical for every installed shop), a valid `(body, hmac)` pair obtained from any one tenant can be replayed against the app's webhook endpoint with a different `shop-domain` header, and `Registry.process` will accept it as authentic for the spoofed shop.

### Finding Description
`Registry.process` (lib/shopify_api/webhooks/registry.rb:188-200) calls `Utils::HmacValidator.validate(request)` to authenticate an inbound webhook. `HmacValidator.validate` (lib/shopify_api/utils/hmac_validator.rb:12-22) computes `HMAC-SHA256(api_secret_key, verifiable_query.to_signable_string)` and compares it to the `hmac` header. `Request#to_signable_string` (lib/shopify_api/webhooks/request.rb:35-38) returns only `@raw_body` — the `shop`, `topic`, and `webhook_id` headers are excluded from the signed content entirely.

After the HMAC check succeeds, `Registry.process` builds `WebhookMetadata` using `request.shop`, which is taken verbatim from the `shopify-shop-domain` header (request.rb:20-23) — a value never covered by the signature. Since the same `Context.api_secret_key` is used to validate webhooks for all shops that install the app (it is not a per-shop secret), the equality the gem should enforce — "the shop this HMAC-authenticated body was sent for" == "the shop the handler is told it came from" — is never checked. An unprivileged user who controls their own installed instance of the app (a real, valid tenant) can capture a legitimately-signed `(raw_body, hmac)` pair from their own shop's webhook delivery and POST it directly to the app's public webhook endpoint with the `shopify-shop-domain` header rewritten to a victim shop's domain. `HmacValidator.validate` still returns `true` because it only checks the body/secret pair, and `Registry.process` dispatches the handler with the attacker-chosen `shop` value.

### Impact Explanation
This breaks the tenant boundary the gem is expected to enforce for webhook processing: the "shop" identity handed to the host application's handler is attacker-controllable despite HMAC validation succeeding, enabling cross-tenant data injection or corruption in any host app that trusts `WebhookMetadata#shop` (e.g., writing order/customer data, inventory updates, or app-uninstall/GDPR events) into the wrong tenant's records.

### Likelihood Explanation
Requires the attacker to be a real (even trial/free) installer of the target app to obtain one valid signed webhook body/HMAC pair for themselves, then a single crafted HTTP POST to the app's public webhook receiving endpoint with a forged `shop-domain` header. No access to `api_secret_key`, tokens, or the target shop is required.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the HMAC-signed payload, or otherwise cryptographically bind the header-derived `shop` value to the signed body before trusting it — e.g., require host applications to independently confirm the shop exists in their session store rather than exposing an unauthenticated `shop` field directly. At minimum, document prominently that `request.shop` is unauthenticated and must not be trusted as a tenant identifier on its own.

### Proof of Concept
```ruby
require "shopify_api"

# 1. Attacker installs the app on their own shop "attacker.myshopify.com" and
#    receives a legitimate webhook delivery, capturing the exact raw body and
#    the "x-shopify-hmac-sha256" header Shopify sent (both valid, since HMAC
#    is computed with the app's single shared client_secret).
raw_body = attacker_captured_raw_body
valid_hmac_b64 = attacker_captured_hmac_header

# 2. Attacker replays the same body+hmac to the app's public webhook endpoint,
#    but swaps the shop-domain header to a victim shop.
forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => valid_hmac_b64,
  "x-shopify-shop-domain" => "victim-shop.myshopify.com",
  "x-shopify-webhook-id" => "forged-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)

# 3. HmacValidator only checks HMAC(api_secret_key, raw_body) == valid_hmac_b64,
#    which is true because raw_body/hmac are unmodified and originally valid.
ShopifyAPI::Webhooks::Registry.process(request)
# => handler.handle is invoked with WebhookMetadata(shop: "victim-shop.myshopify.com", ...)
#    even though this payload never actually came from victim-shop.
``` [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-30)
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
```
