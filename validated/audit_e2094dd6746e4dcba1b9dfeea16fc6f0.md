### Title
Webhook `shop` (and `topic`/`webhook_id`) identity fields are not covered by the HMAC signature, enabling cross-tenant webhook spoofing via replay - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC computed over the raw request body, then unconditionally trusts the `shop-domain`, `topic`, and `webhook-id` values taken from HTTP headers to build the `WebhookMetadata` object dispatched to the app's handler. Because those identity fields are never part of the signed content, an attacker who has legitimately received one webhook (with a valid body+HMAC pair, e.g. by triggering an event in a store they control that has the app installed) can replay that exact body/HMAC to the app's public webhook endpoint while substituting a different shop's domain in the header. The signature still validates because it never covered the shop identity, so the handler processes attacker-controlled data as if it belonged to an arbitrary victim shop.

### Finding Description
The identity binding that should hold is:
`shop bound by the HMAC == shop the handler attributes the payload to`

In this gem that equality is broken:
- `Request#hmac` decodes the `x-shopify-hmac-sha256` header and `Request#to_signable_string` returns only `@raw_body`: [1](#0-0) [2](#0-1) 
- `Request#shop`, `#topic`, and `#webhook_id` are read straight from unauthenticated headers with no cryptographic tie to the body: [3](#0-2) 
- `HmacValidator.validate` / `validate_signature` compute and compare the HMAC only against `verifiable_query.to_signable_string` (i.e., the raw body), never incorporating `shop`, `topic`, or `webhook_id`: [4](#0-3) 
- `Registry.process` gates entirely on that body-only HMAC check and then forwards the unauthenticated `request.shop`/`request.topic`/`request.webhook_id` straight into `WebhookMetadata` for the app's handler to act on: [5](#0-4) 

Before the attacker's request: for a legitimately delivered webhook, `header.shop == data.shop` and both are consistent with the body's true origin shop because Shopify itself only ever sends that combination together.

After the attacker's replay: the attacker resends the exact same `raw_body`/`hmac` pair (captured from a webhook Shopify sent for a shop the attacker controls) but swaps `x-shopify-shop-domain` (and optionally `x-shopify-topic`) to point at a victim shop. `Utils::HmacValidator.validate` still returns `true` because it only re-derives the HMAC from `@raw_body`, so `header.shop` (victim) is accepted while the body content still belongs to the attacker's own shop — the equality is broken.

### Impact Explanation
This crosses a tenant boundary without any credential from the victim: the app's handler receives `WebhookMetadata` claiming to be from the victim shop but carrying attacker-chosen body content, letting an unprivileged internet user inject cross-tenant data/events into another merchant's context that the host app trusts as authentic per-shop webhook data.

### Likelihood Explanation
The prerequisite is low: any actor who can install the app on a shop they control (or otherwise trigger one genuine webhook delivery to the app, e.g. via a free trial/dev store) obtains a valid `(raw_body, hmac)` pair usable for replay, since the signature never binds to shop/topic. No `api_secret_key`, access token, or victim credentials are required — only the ability to POST to the app's public webhook endpoint with modified headers.

### Recommendation
Bind the shop/topic/webhook identity into the authenticated data path: either include `shop`, `topic`, and `webhook_id` in the signable string used by `HmacValidator`, or have `Registry.process` independently verify that the shop asserted in headers matches the shop the current session/installation record expects before dispatching to a handler, rejecting mismatches instead of trusting header-derived identity unconditionally.

### Proof of Concept
1. Install/operate the target app on `attacker-shop.myshopify.com` and trigger any subscribed webhook topic (e.g., `orders/create`) to receive a genuine webhook: raw body `B`, headers including `x-shopify-hmac-sha256: H`, `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Replay a crafted HTTP POST to the app's public webhook endpoint using the same body `B` and the same `H`, but set `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only and matches `H`, so validation succeeds: [6](#0-5) 
4. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and body content originating from the attacker's shop, demonstrating the identity-binding break: [7](#0-6)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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
