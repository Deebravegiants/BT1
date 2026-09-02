### Title
Webhook `shop`, `topic`, `webhook-id`, and `api-version` headers are trusted for tenant attribution without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC that `Utils::HmacValidator.validate` checks in `Registry.process` never covers the `shop`, `topic`, `webhook-id`, or `api-version` header values that are subsequently trusted and handed to the app's webhook handler as the tenant/topic identity.

### Finding Description
`Webhooks::Registry.process` authenticates an inbound webhook solely via `Utils::HmacValidator.validate(request)`: [1](#0-0) [1](#0-0) 

That validator computes an HMAC over `verifiable_query.to_signable_string` and compares it with `verifiable_query.hmac`: [2](#0-1) 

For `Webhooks::Request`, `to_signable_string` returns only `@raw_body`: [3](#0-2) 

while `shop`, `topic`, `webhook_id`, and `api_version` are all read directly and unauthenticated from HTTP headers: [4](#0-3) 

`Registry.process` then trusts `request.shop` and `request.topic` (neither bound by the signature) to select the handler and build the `WebhookMetadata` passed to the app's business logic: [5](#0-4) 

The binding that should hold is: `hmac == HMAC(secret, body ‖ shop ‖ topic)`, i.e. the tenant/topic attribution should be cryptographically bound to the same value that is authenticated. Instead the equality actually enforced is `hmac == HMAC(secret, body)`, with `shop`/`topic` supplied out-of-band and never checked against the signature. Any party capable of producing a validly-signed body for the shared `api_secret_key` — which is identical for every shop that installs the app, not shop-specific — can attach an arbitrary `x-shopify-shop-domain` header to a signed body and have the app process it as if it originated from a different, unrelated tenant.

### Impact Explanation
Because `api_secret_key` is a single app-level secret shared across every shop that installs the app, an unprivileged shop owner who installs the app can legitimately receive genuinely-signed webhook deliveries (body + `hmac-sha256`) for their own store. Since the signature covers only the body, that same signed body/HMAC pair remains valid when replayed with the `x-shopify-shop-domain` header (and/or `x-shopify-topic`) changed to name a different, victim shop. `Registry.process` will accept it (`Utils::HmacValidator.validate` passes) and dispatch the handler with `WebhookMetadata#shop` set to the attacker-chosen victim domain, causing the host application to attribute the webhook's data/side effects to the wrong tenant. This is a cross-tenant confusion primitive reachable by any low-privileged shop that has merely installed the app — matching the Critical "cross-tenant access" impact category, since it lets one tenant's authenticated event stream be attributed to and acted upon under another tenant's identity.

### Likelihood Explanation
Any shop that installs the app is an "unprivileged internet user" relative to other tenants, and receiving at least one genuine webhook for their own store (e.g. `orders/create`) is a normal, unavoidable part of using the app — this is trivially obtainable, not a theoretical precondition. Forging the header value requires no cryptographic secret at all beyond the already-obtained genuine signature/body pair. The only precondition is that the host application relies on `WebhookMetadata#shop`/`#topic` (as returned by this gem) to determine which tenant a webhook affects — which is exactly the documented and expected usage pattern of `Webhooks::Registry.process`/`WebhookHandler#handle`.

### Recommendation
Bind the identity fields used by consumers into the signed content, or verify them out of band before trusting them: e.g. extend `Webhooks::Request#to_signable_string` (or add a secondary check in `Registry.process`) to require that the `shop` header matches an expected/installed shop for the given `api_secret_key`/session, or otherwise ensure the app cannot select behavior purely from the unauthenticated `shop`/`topic` headers. At minimum, document prominently that `WebhookMetadata#shop` is not authenticated by the HMAC and must be independently corroborated (e.g. against a known installed-shop list) before being used for tenant-scoped side effects.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` (this only requires being a normal merchant, no elevated privilege).
2. Shopify delivers a genuine webhook to the app, e.g.:
   ```
   POST /webhooks
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <valid HMAC of body computed with the app's shared api_secret_key>
   x-shopify-shop-domain: attacker.myshopify.com
   Body: {"id": 1, "note": "malicious payload chosen by attacker within their own store's order fields"}
   ```
3. Attacker captures this body and its `x-shopify-hmac-sha256` value unchanged, and replays the exact same request to the app's webhook endpoint but with:
   ```
   x-shopify-shop-domain: victim.myshopify.com
   ```
   leaving the body and HMAC identical.
4. `Utils::HmacValidator.validate` in `hmac_validator.rb` recomputes the HMAC over the (unchanged) body only and it matches, so `Registry.process` in `registry.rb` accepts the request and invokes the registered handler with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)`, causing the app to apply attacker-controlled body content under the victim shop's identity.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
