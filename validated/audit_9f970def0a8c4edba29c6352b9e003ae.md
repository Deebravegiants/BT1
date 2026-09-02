Confirmed: the `shop-domain` header is never part of the HMAC-signed payload.

### Title
Cross-tenant webhook spoofing via unauthenticated `shop-domain` header - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then reads the `shop` (from the `x-shopify-shop-domain`/`shopify-shop-domain` header) and forwards it—unverified—to the app's registered handler as trusted tenant identity. Because the HMAC signature never covers the shop header, any request with a validly-signed body can carry an arbitrary shop domain, breaking the binding `shop authenticated == shop the handler trusts`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` computes/verifies the HMAC exclusively against `to_signable_string`, i.e. the body: [2](#0-1) 

`Registry.process` validates the HMAC and then, using `request.shop` (read from the unsigned header) constructs the `WebhookMetadata` that is delivered to the app's handler as the authenticated tenant identifier: [3](#0-2) 

`request.shop` itself is read straight from the header with no cross-check against anything cryptographically bound to that shop: [4](#0-3) 

Since Shopify apps typically share one `api_secret_key`/HMAC secret across all shops that install the app (it's the app-level client secret, not a per-shop secret), an attacker who legitimately installs the target app on their own (attacker-controlled) shop will receive real, validly-signed webhook deliveries for their own shop. Because the signature covers only the body — not the shop header — the attacker can capture one such delivery and replay it to the app's webhook endpoint with the `x-shopify-shop-domain` header rewritten to a victim shop's domain. `HmacValidator.validate` still succeeds (the body and signature are untouched and were generated with the same shared secret), so `Registry.process` calls the handler with `WebhookMetadata#shop` set to the victim's domain instead of the attacker's own. The equality the code implicitly assumes — "the shop whose secret validated this HMAC" == "the shop named in `request.shop`" — does not hold, because no per-shop material participates in the signature at all; the signing key and the signed content say nothing about which shop is being claimed.

### Impact Explanation
Handler implementations documented by this gem (`docs/usage/webhooks.md`) use `data.shop` as the authoritative tenant key to route webhook payloads to the correct merchant's data/queue: [5](#0-4) 

An attacker who is a legitimate (if low-privilege) installer of the app can therefore inject arbitrary attacker-controlled webhook bodies that get attributed to a victim shop of their choosing, corrupting that other tenant's data pipeline (e.g. spoofed `orders/create`, `customers/data_request`, `shop/redact` events) — a cross-tenant integrity/confidentiality violation qualifying as Critical cross-tenant access.

### Likelihood Explanation
Exploitation only requires the attacker to install the target app on any shop they control (a normal, unprivileged action for any Shopify merchant/developer) and to be able to send an HTTP POST with edited headers to the app's public webhook endpoint. No access token, `api_secret_key`, or other secret is needed beyond what a legitimate low-privilege installer already possesses through normal app installation.

### Recommendation
Bind the shop identity into the HMAC-covered signable content (e.g. include `shop-domain`, `topic`, and `webhook_id` in `to_signable_string`, matching Shopify's webhook signing scheme if it supports this) or, at minimum, cross-validate `request.shop` against a known/expected set of shops (e.g. those with active registrations/sessions) before trusting it in `WebhookMetadata`. Document explicitly that `request.shop` is not itself HMAC-protected apart from the body, so host applications cannot mistakenly treat it as a verified tenant identifier.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`, receiving genuine webhook deliveries (e.g. `orders/create`) signed with the app's shared `api_secret_key` over the JSON body.
2. Attacker captures one such delivery: raw body `B`, header `x-shopify-hmac-sha256: H` (valid HMAC of `B`), `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker replays the same body `B` and signature `H` to the app's webhook endpoint but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` succeeds because it only checks `HMAC(secret, B) == H`, which is unchanged.
5. `Registry.process` calls the app's handler with `WebhookMetadata.shop == "victim-shop.myshopify.com"`, causing the app to process attacker-supplied data as if it originated from the victim tenant.

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

**File:** docs/usage/webhooks.md (L19-30)
```markdown
```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```
```
