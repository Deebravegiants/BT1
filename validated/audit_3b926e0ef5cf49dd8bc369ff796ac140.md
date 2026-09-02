## Finding: Webhook `shop` (and `topic`/`webhook_id`) fields are trusted from headers but are not covered by the HMAC signature check

### Title
Cross-tenant webhook spoofing via unauthenticated `shop-domain` header not covered by HMAC verification - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body, then dispatches the handler using the `shop`, `topic`, and `webhook_id` values taken directly from HTTP headers — none of which are included in the signed content. This breaks the equality that should hold between "bytes verified" and "bytes/fields acted on."

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

while `shop`, `topic`, and `webhook_id` are read from HTTP headers that are never fed into the signed string: [2](#0-1) 

`Utils::HmacValidator.validate` only checks `verifiable_query.hmac` against a signature computed over `to_signable_string` (i.e. the body): [3](#0-2) 

`Registry.process` then dispatches to the handler with `request.shop` after only this body-only HMAC check passes — there is no additional check binding the `shop` header to the signature: [4](#0-3) 

Equality that should hold: `bytes_verified_by_hmac == bytes_the_handler_trusts_for_tenant_attribution`. In reality: `bytes_verified_by_hmac (raw_body) ≠ bytes_the_handler_trusts_for_tenant_attribution (raw_body + shop header + topic header + webhook_id header)`. The `shop` field — the tenant identity binding used by the handler (`WebhookMetadata.new(... shop: request.shop ...)`) — is completely outside the authenticated envelope.

### Impact Explanation
An unprivileged internet user who operates their own Shopify store (obtainable without any privileged credentials) receives genuine, validly-HMAC-signed webhooks from Shopify for their own store. Because the signature covers only the body, that same `(body, hmac)` pair remains valid regardless of the `shop-domain` header value sent alongside it. The attacker can replay the identical body+HMAC to the app's webhook endpoint while substituting the `shop-domain` header for a victim shop's domain. `Registry.process` will pass HMAC validation and hand the handler a `WebhookMetadata` object asserting the data belongs to the victim shop, when it is actually the attacker's own (possibly attacker-crafted) data. Depending on how the host application persists/act on webhook payloads keyed by `shop`, this enables cross-tenant data injection/confusion (e.g., writing attacker-controlled data under the victim shop's tenant record) — a cross-tenant access violation.

### Likelihood Explanation
Likelihood is moderate: no access token, `client_secret`, or TLS interception is required. The only prerequisite is the attacker having their own store connected to the target app (trivial, since Shopify dev stores are freely obtainable), from which they harvest a legitimate `(raw_body, hmac)` pair, then send a crafted HTTP request to the app's public webhook endpoint with an arbitrary `shop-domain` header.

### Recommendation
Include the `shop` (and ideally `topic`/`webhook_id`) header value in the signable string used for HMAC verification, or otherwise cryptographically bind them to the request (e.g., verify the `shop` header corresponds to a shop with an active, stored session/subscription for that specific webhook topic before dispatching), rather than trusting the header value merely because the body's HMAC is valid.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and receives a real webhook, capturing the raw body `B` and the valid `X-Shopify-Hmac-Sha256` header `H` (computed by Shopify over `B` with the app's real secret).
2. Attacker sends:
```
POST /webhooks HTTP/1.1
X-Shopify-Topic: orders/create
X-Shopify-Hmac-Sha256: H
X-Shopify-Shop-Domain: victim-shop.myshopify.com
Content-Type: application/json

B
```
3. `ShopifyAPI::Webhooks::Registry.process` computes the HMAC over `B` only via `Utils::HmacValidator.validate`, which succeeds since `B`/`H` are a valid pair.
4. The handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, even though the actual data originated from the attacker's own store.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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
