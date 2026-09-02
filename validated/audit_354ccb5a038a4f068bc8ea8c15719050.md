### Title
Webhook HMAC only signs the raw body, so the `shop`, `topic`, and `webhook-id` headers used for tenant routing are unauthenticated - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` implements `VerifiableQuery#to_signable_string` by returning only the raw HTTP body, while `shop`, `topic`, and `webhook_id` are read straight from HTTP headers with no binding to the signature. `Registry.process` validates the HMAC against the body only and then forwards the header-derived `shop` value to the app's handler as the trusted tenant identifier, breaking the equality `shop_verified_by_hmac == shop_used_for_business_logic`.

### Finding Description
`Request#to_signable_string` returns `@raw_body` exclusively: [1](#0-0) 

`Request#shop`, `#topic`, and `#webhook_id` are parsed directly out of headers and are never part of the signed payload: [2](#0-1) 

`Registry.process` validates only the body via `Utils::HmacValidator.validate(request)`, and then constructs `WebhookMetadata` using the unauthenticated `request.shop`/`request.topic`/`request.webhook_id`, passing it to the app's handler as if it were verified: [3](#0-2) 

`Utils::HmacValidator.validate_signature` computes the HMAC purely from `verifiable_query.to_signable_string` (the body), so it can only ever prove "this body was produced with the app's secret" - it proves nothing about which shop sent it: [4](#0-3) 

Because the app's `client_secret`/`api_secret_key` is shared across every shop that has the app installed, any merchant who has the app installed on their own store legitimately receives real `(raw_body, hmac)` pairs. That merchant can capture one of these valid pairs and replay it to the same webhook endpoint while substituting the `shopify-shop-domain` (and/or `shopify-topic`/`shopify-webhook-id`) header for a victim shop. `HmacValidator.validate` will still pass, because the header content it changed was never part of the signed string, yet `Registry.process` will hand the handler a `WebhookMetadata` object claiming the body belongs to the victim shop.

### Impact Explanation
This breaks the tenant-identity binding the HMAC is supposed to establish: verified bytes (the body) are decoupled from the acted-upon identity (the `shop` header). A merchant who legitimately controls one tenant can cause the app to process attacker-supplied webhook content under a different, unauthorized tenant's identity - a cross-tenant confusion/spoofing primitive reachable purely by replaying already-signed traffic they legitimately received, with no access to the app's secret. Depending on how the host app uses `WebhookMetadata#shop` (e.g., to select which shop's stored access token/session to act on, or which tenant's records to update), this can escalate to cross-tenant data corruption or unauthorized actions performed against a shop the attacker does not control.

### Likelihood Explanation
Any user who can install the target app on their own store (a routine, unprivileged action for a Shopify merchant) automatically receives legitimately HMAC-signed webhook traffic they can capture and replay with modified headers. No credential theft, TLS interception, or privileged access is required - only ordinary use of the webhook feature as documented by this gem.

### Recommendation
Bind the header-derived identifiers into the signed payload validation, e.g., require the host application (or the gem itself) to independently corroborate `shop`/`topic`/`webhook_id` against a known, previously-registered webhook subscription or against shop-scoped session state before trusting them, rather than trusting raw headers whenever the body-only HMAC check succeeds. At minimum, the gem's documentation and `WebhookMetadata` API should make explicit that `shop`, `topic`, and `webhook_id` are unauthenticated header values not covered by the HMAC, so host applications don't implicitly treat them as verified tenant identity.

### Proof of Concept
1. Install the target Shopify app on attacker-controlled Shop A; the app's webhook endpoint receives a legitimate webhook request with a real `shopify-hmac-sha256` header computed over some `raw_body` using the app's shared `api_secret_key`.
2. Capture this `(raw_body, hmac)` pair (e.g., from attacker's own server logs/network trace of traffic addressed to their own installed app).
3. Replay an HTTP POST to the same webhook endpoint using the identical `raw_body` and `shopify-hmac-sha256` header, but set `shopify-shop-domain` (and optionally `shopify-topic`) to Shop B's domain.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `raw_body` against the secret: [5](#0-4) 
5. The handler receives `WebhookMetadata` with `shop: "shop-b.myshopify.com"` and processes attacker-controlled `raw_body` content as if it were an authentic webhook from Shop B.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
