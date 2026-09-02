## Title
Webhook `shop` (and `topic`/`webhook-id`) headers are not covered by the HMAC signature, allowing a malicious merchant to relay a genuine webhook and spoof the tenant it is attributed to - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw request body, so the HMAC computed by `ShopifyAPI::Utils::HmacValidator.validate` only authenticates the *body* bytes, never the `shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`, or `shopify-api-version` headers. `ShopifyAPI::Webhooks::Registry.process` nonetheless trusts `request.shop` (taken straight from the unauthenticated header) and hands it to the app's handler as the tenant identifier. Because Shopify signs webhooks with the app-wide `client_secret` (the same secret for every shop that installs the app), any merchant who installs the app can legitimately receive a validly-signed webhook for their own shop and then replay that exact body+HMAC pair to the app's public webhook endpoint while substituting a victim shop's domain in the `shopify-shop-domain` header. The signature check still passes because the body and HMAC were untouched; only the header, which is unauthenticated, changed.

### Finding Description
- `to_signable_string` in `lib/shopify_api/webhooks/request.rb` (lines 35-38) returns `@raw_body` exclusively: [1](#0-0) 
- `shop`, `topic`, `api_version`, and `webhook_id` are all read directly from HTTP headers, independent of the signed payload: [2](#0-1) 
- `HmacValidator.validate_signature` computes the signature only from `verifiable_query.to_signable_string` (i.e. the body for webhooks) and compares it against the `hmac` field: [3](#0-2) 
- `Registry.process` gates on that HMAC check alone, then forwards the unauthenticated `request.shop` value straight into the handler's `WebhookMetadata`, with no cross-check against the shop that actually owns the webhook subscription/session: [4](#0-3) 

The binding that is broken is:
`shop used to attribute/act on the webhook (request.shop header)` ≠ `shop actually covered by the cryptographic signature (HMAC over raw_body only)`.

Since the webhook signing secret is the app's single `client_secret`, shared across all merchants who install the app, this is not merely a theoretical "bytes verified vs. bytes parsed" gap — it is directly exploitable by any unprivileged merchant that can install the app for their own shop, obtain a genuine signed webhook, and then re-POST it to the same public endpoint with a different `shopify-shop-domain` header pointing at a victim tenant. The HMAC check in `Registry.process` still succeeds because it only validates the byte-for-byte body, and the app-level handler will process the event as if it belongs to the victim's tenant.

### Impact Explanation
This crosses a tenant boundary using only unprivileged capabilities (installing the app on one's own store is the normal, self-service onboarding flow for a Shopify app), matching the "Critical - cross-tenant access" impact bucket in the rules: the attacker can make the app record/act on webhook data (e.g. `orders/create`, `customers/data_request`, etc.) as though it originated from an arbitrary victim shop, without ever needing the victim's credentials, session, or the app's `client_secret`.

### Likelihood Explanation
Any developer/merchant able to install the target app on a shop they control satisfies all prerequisites: they get a validly signed webhook for free, and only need to alter one unauthenticated header before re-sending the request to the app's known public webhook URL. No secret material, session hijacking, or privileged access is required.

### Recommendation
Bind the shop identity cryptographically to the signed payload rather than trusting the `shopify-shop-domain` (and other Shopify-*) headers implicitly:
- Include the shop domain (and ideally topic/webhook id) in the signable string used for HMAC verification, or
- After HMAC validation, independently verify that the `shop` header matches a shop that has an active, registered subscription for that `webhook_id`/topic (e.g. via a lookup against stored sessions/subscriptions) before invoking the handler, rejecting the webhook if the header-derived shop cannot be corroborated.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` (self-service, no special privileges).
2. Attacker triggers a real event (e.g., creates an order) causing Shopify to POST a genuine `orders/create` webhook to the app's public callback URL, with headers:
   - `x-shopify-shop-domain: attacker-shop.myshopify.com`
   - `x-shopify-hmac-sha256: <valid signature of raw body under app's client_secret>`
3. Attacker captures this exact HTTP request (body + `x-shopify-hmac-sha256` unchanged) and replays it to the same webhook endpoint, only modifying:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (== the unchanged raw body) and finds it matches — validation passes.
5. `Registry.process` invokes the app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: "orders/create", body: <attacker's own order payload>, ...)`, causing the app to process/store data as if it belongs to `victim-shop`.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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
