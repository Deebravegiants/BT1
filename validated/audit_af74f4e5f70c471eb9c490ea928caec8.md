## Title
Webhook `shop-domain` and `topic` headers are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, while the `shop`, `topic`, and `webhook_id` values used by the application to route and attribute the webhook are read directly from unauthenticated HTTP headers. `Utils::HmacValidator.validate` only proves that the *body* was signed by Shopify with the app's secret; it proves nothing about which shop or topic that signature was meant for. An attacker who can obtain any one legitimately HMAC-signed body/signature pair (e.g., by installing the app on their own store and receiving their own webhooks) can replay that exact body+signature to the app's webhook endpoint while substituting the `shop-domain`/`topic` headers for a victim shop, and the signature check will still pass.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, and `webhook_id` are pulled straight from HTTP headers with no cryptographic binding to the signed content: [2](#0-1) 

`Registry.process` validates the request purely via `HmacValidator.validate(request)`, then constructs `WebhookMetadata` using the unauthenticated `request.shop` and `request.topic` values and dispatches it to the app's handler: [3](#0-2) 

`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` (the raw body) and compares it to the received signature — it never incorporates the shop or topic into what is verified: [4](#0-3) 

The broken identity binding is:
`shop-header-claimed-by-request == shop-that-the-HMAC-signed-body-actually-belongs-to`

Before the attack: a legitimate webhook for Shop A arrives with `shop-domain: A.myshopify.com`, body `B`, and `hmac = HMAC(secret, B)`. The app correctly attributes body `B` to Shop A.

After the attacker's request: the attacker (who has legitimately received their own `(B, hmac)` pair from their own store, or captured one via any means not requiring `api_secret_key`) POSTs the same `B` and `hmac` to the app's public webhook endpoint, but sets `shop-domain: VictimShop.myshopify.com`. `HmacValidator.validate` still succeeds because it only checks `HMAC(secret, B) == hmac`, and `Registry.process` proceeds to call the handler with `shop: "VictimShop.myshopify.com"`. The app now processes attacker-controlled/replayed data as if it originated from the victim tenant — the topic and shop fields are "acted on but not covered by the HMAC."

### Impact Explanation
This crosses a tenant boundary without any credential belonging to the victim: an app that uses `shop` (and/or `topic`) from `WebhookMetadata` to select which merchant's data to create, update, or delete (a standard pattern for multi-tenant Shopify apps) can be made to apply attacker-supplied webhook bodies to a different, victim shop's tenant context. Depending on the handler's use of the topic (e.g. `app/uninstalled`, `shop/redact`, `customers/data_request`), this can trigger destructive or data-exposing actions against a shop the attacker does not control — a cross-tenant access impact.

### Likelihood Explanation
High. Any user can freely install the target app on their own development/free-trial store (no privileged credentials required) and thereby legitimately receive valid `(raw_body, hmac)` pairs signed with the app's real secret. Because the header fields are excluded from the signed content, forging the `shop-domain`/`topic` headers on a replayed request requires no cryptographic material — this is a straightforward unauthenticated HTTP request substitution.

### Recommendation
Bind the routing/attribution fields to the signature. Either:
- Include `shop`, `topic`, and `webhook_id` in `to_signable_string` (would require coordinating with Shopify's HMAC generation), or, more practically,
- Have `Registry.process` cross-check that the `shop` reported by the webhook matches the shop the receiving endpoint/session is scoped to (e.g., compare against the app's own session-derived shop for that endpoint) before dispatching to the handler, rather than trusting the header value implicitly.
- At minimum, document clearly that `request.shop`/`request.topic` are unauthenticated header values and must not be used as the sole tenant-scoping key without an independent binding check.

### Proof of Concept
```ruby
# 1. Attacker installs the app on their own shop "attacker.myshopify.com"
#    and receives a legitimate webhook:
raw_body = '{"id": 1}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, raw_body)

# 2. Attacker replays the exact same body+hmac to the app's public
#    webhook endpoint, but swaps the shop-domain header to the victim shop:
headers = {
  "x-shopify-topic" => "app/uninstalled",       # or any topic the app registers
  "x-shopify-hmac-sha256" => Base64.encode64(hmac),
  "x-shopify-shop-domain" => "victim-shop.myshopify.com",  # spoofed
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)

# 3. HMAC validation succeeds because only raw_body is checked:
ShopifyAPI::Utils::HmacValidator.validate(request) # => true

# 4. Registry.process dispatches to the handler with shop = "victim-shop.myshopify.com",
#    even though that shop never sent this webhook.
ShopifyAPI::Webhooks::Registry.process(request)
```

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
