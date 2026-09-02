Confirmed: `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) validates the HMAC via `Utils::HmacValidator.validate(request)`, then builds `WebhookMetadata` using `request.shop` — but `Request#to_signable_string` (`lib/shopify_api/webhooks/request.rb:35-38`) returns only `@raw_body`, never mixing in the `shop-domain`, `topic`, or `webhook-id` headers. This is the identity-binding break the report's bug class maps to in this gem.

### Title
Webhook `shop-domain` header is trusted for tenant identity without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body alone, while the `shop`, `topic`, and `webhook_id` values used by the host application's webhook handler come from separate, unsigned HTTP headers. Anyone who can obtain one validly-signed webhook body (e.g., a merchant receiving real webhooks for their own installed shop) can replay that exact body to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header for a different shop, and the HMAC check still passes because the header is never part of the signed bytes.

### Finding Description
`Request#to_signable_string` only returns `@raw_body`: [1](#0-0) 
while `shop`, `topic`, and `webhook_id` are parsed straight from headers with no cryptographic linkage to the body: [2](#0-1) 

`Registry.process` validates only the HMAC of the request (i.e., of the body) and then trusts `request.shop`/`request.topic`/`request.webhook_id` directly to build the `WebhookMetadata` handed to the app's registered handler: [3](#0-2) 

The broken identity binding is: `HMAC-verified bytes (raw_body only) ≠ bytes acted on (raw_body + shop-domain header)`. Because `shop` is acted upon (attributed to a specific merchant/tenant) but not included in the signed content, an attacker who possesses one legitimately-signed webhook payload (trivially obtainable by installing the app on their own store and receiving a real webhook) can resend that identical body with an altered `shop-domain` header, and the gem will report it as successfully HMAC-validated and hand it to the handler labeled with the attacker-chosen shop.

### Impact Explanation
This crosses a tenant boundary: the host application's webhook handler receives shop-attributed data (`WebhookMetadata#shop`) it did not actually get from that shop, without any cryptographic guarantee tying the shop identity to the payload. Depending on how the host app uses `data.shop` (e.g., looking up which merchant's local records to update/delete, as is typical for `shop/redact`, `app/uninstalled`, order or product webhooks), this enables cross-tenant data corruption or spoofed lifecycle events attributed to a victim shop — satisfying the "cross-tenant access" criterion. No `api_secret_key`, access token, or privileged account is required; the only prerequisite is a validly-signed sample payload the attacker can generate themselves via their own (unprivileged) shop.

### Likelihood Explanation
Low-to-moderate: it requires the attacker to first obtain any one genuine, HMAC-valid webhook body of their choosing (easy — install the app on their own store, trigger the relevant event) and then replay it with a forged `shop-domain` header to the app's public webhook endpoint. It does not require guessing any secret or bypassing HMAC verification itself, only the missing header binding.

### Recommendation
Include `shop`, `topic`, and `webhook_id` (or at minimum `shop`) in the HMAC-signed content, or otherwise cryptographically bind the header-derived identity to the request body before it is trusted — mirroring how `Auth::Oauth::AuthQuery#to_signable_string` binds `shop` into its signable string.

### Proof of Concept
1. Attacker installs the app on their own store `attacker.myshopify.com` and lets it deliver a real webhook (e.g., `orders/create`) — capturing the raw request body `B` and its valid `X-Shopify-Hmac-Sha256` header `H` (computed by Shopify over `B` using the app's `client_secret`, which the attacker never needs to know).
2. Attacker resends a POST to the app's webhook endpoint with the identical body `B`, identical `H`, but with `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate(request)` calls `request.to_signable_string`, which returns only `B`; the HMAC check succeeds because it never depended on the shop header. [4](#0-3) 
4. `Registry.process` proceeds to call the registered handler with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", ...)`, even though the payload never originated from that shop. [5](#0-4)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
```
