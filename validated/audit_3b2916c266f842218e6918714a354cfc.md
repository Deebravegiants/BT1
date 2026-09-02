### Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, but the `shop` value that is handed to the app's webhook handler is read from an HTTP header that is never included in the signed material. Because a single app-wide secret (`Context.api_secret_key`) produces the same signature for the same body regardless of which shop the header claims to be from, any holder of one legitimately-signed `(body, hmac)` pair — obtainable simply by installing the app on any shop the attacker controls — can replay that pair to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header changed to a victim shop, and the signature will still validate.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read from a separate, unsigned header: [2](#0-1) 

`Registry.process` validates the HMAC over `request` (i.e., over `raw_body` only) and then trusts `request.shop` as the tenant identity forwarded to the handler: [3](#0-2) 

`HmacValidator.validate` computes the signature strictly from `verifiable_query.to_signable_string`, so it never incorporates the `shop-domain` header: [4](#0-3) 

This is exactly the reported bug class: a field that is *acted on* (the `shop` used to key `WebhookMetadata` and dispatched to the handler) is not covered by the cryptographic check that is supposed to prove the message's authenticity/origin — analogous to `burn()` operating on an address that was never checked against the caller.

### Impact Explanation
Because the webhook secret (`api_secret_key`) is shared across every shop that has the app installed, an attacker does not need the secret itself: they only need one valid `(raw_body, hmac)` pair, which Shopify will hand them for free the moment they install the app on any store they control (including a free development store). They can then POST that exact `raw_body` and `hmac` to the app's public webhook endpoint while substituting `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) with a victim shop's domain. `Registry.process` will validate the HMAC (it only checks the body) and dispatch `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` to the app's handler, which will act as though the victim shop sent that event. Depending on how the host application uses `shop` (e.g., looking up/mutating the victim's stored session, triggering shop-scoped business logic, writing victim-shop-keyed data), this crosses the tenant boundary — satisfying the "cross-tenant access" criticality bar.

### Likelihood Explanation
The only prerequisite is the ability to install the app on any shop (trivial for a developer store) and observe one webhook. No leaked credentials, `api_secret_key`, or access tokens are required, and the replay/tamper is a simple HTTP POST with a modified header — well within reach of an unprivileged actor.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the signed material, or otherwise cryptographically tie the header-derived tenant identity to the HMAC-verified payload — e.g., require the body to embed the shop domain and cross-check it against the header before trusting `request.shop`, or document/enforce that consuming apps must independently verify `shop` against their own installed-shop registry rather than relying on `HmacValidator.validate` to vouch for it.

### Proof of Concept
1. Install the target app on an attacker-controlled shop `attacker.myshopify.com`; trigger any webhook (e.g., `orders/create`) and capture the raw POST: body `B` and header `X-Shopify-Hmac-Sha256: H` (valid because `H = HMAC-SHA256(api_secret_key, B)`).
2. Replay to the same app's public webhook endpoint:
```
POST /webhooks HTTP/1.1
X-Shopify-Topic: orders/create
X-Shopify-Hmac-Sha256: H
X-Shopify-Shop-Domain: victim-shop.myshopify.com
X-Shopify-Webhook-Id: <any>
X-Shopify-Api-Version: 2024-01
Content-Type: application/json

B
```
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `B` against `H`, per `lib/shopify_api/utils/hmac_validator.rb` and `lib/shopify_api/webhooks/request.rb`.
4. The handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, letting the attacker inject events attributed to a shop they do not own or control.

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
