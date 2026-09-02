## Analysis

I found a concrete analog of the "signature check doesn't bind what the code trusts" bug class in the webhook processing path.

### Title
Webhook `shop-domain` (and `topic`/`webhook-id`/`api-version`) headers are trusted for tenant attribution but are not covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body, while `ShopifyAPI::Webhooks::Registry.process` trusts `request.shop` (parsed straight from an HTTP header) as the tenant identity for the webhook handler, without that value ever being covered by the HMAC that the gem validates.

### Finding Description
`Registry.process` validates the webhook solely via `Utils::HmacValidator.validate(request)`, then hands the handler a `WebhookMetadata` built from `request.shop`, `request.topic`, etc.: [1](#0-0) 

`HmacValidator` verifies `verifiable_query.hmac` against `compute_signature(verifiable_query.to_signable_string, secret)`: [2](#0-1) 

But `Request#to_signable_string` returns only `@raw_body` - it never includes the `shop`, `topic`, `webhook-id`, or `api-version` headers: [3](#0-2) 

Those same unauthenticated header values are exactly what `shop`, `topic`, and `webhook_id` return and what gets passed into `WebhookMetadata` for the handler to act on: [4](#0-3) [5](#0-4) 

The binding that should hold is: `shop that produced the HMAC-valid body == shop attributed to the webhook by the handler`. Because `shop` is outside the signed bytes, this equality is not enforced.

Crucially, this is exploitable in a multi-tenant setting because the HMAC secret (`Context.api_secret_key`) is the app's single, shop-independent secret, not a per-shop secret. Any user who installs the app on their own store legitimately receives real Shopify webhooks with a valid `(body, hmac)` pair for that body. Since the `shop-domain` header (and `topic`/`webhook-id`) are not part of the signed bytes, that same `(body, hmac)` pair remains valid if re-sent to the app's public webhook endpoint with the `shop-domain` header swapped to a different (victim) shop.

### Impact Explanation
This crosses a tenant boundary: an unprivileged app user (merchant who installed the app on their own store) can produce a request that the gem certifies as HMAC-valid while the `shop` value processed by the handler is an arbitrary victim shop. Any host application logic keyed off `WebhookMetadata#shop` (e.g., "look up the victim's session/access token and act on their behalf using the delivered body", or "attribute/write body data under the victim's tenant record") can be corrupted or hijacked this way, i.e. cross-tenant access/impact.

### Likelihood Explanation
Requires only: (1) attacker installs the app on their own (attacker-controlled) shop to legitimately receive one HMAC-signed webhook, and (2) attacker sends an HTTP POST directly to the app's public webhook endpoint with the same raw body/HMAC but a victim `shop-domain` header. No access token, `client_secret`, or privileged access is required - only the ability to install the app once and send a normal HTTP request, which matches an "unprivileged internet user" threat model.

### Recommendation
Include the identifying headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the signable string used for HMAC computation, or otherwise cryptographically bind them to the body before `to_signable_string` is used in `HmacValidator.validate`, so a re-signed body can't be replayed under a different shop's identity.

### Proof of Concept
1. Install the app on attacker-owned shop `attacker.myshopify.com`; capture a real webhook delivery: raw body `B`, headers include `x-shopify-hmac-sha256: H` (valid for `B`) and `x-shopify-shop-domain: attacker.myshopify.com`.
2. Send a new HTTP request directly to the app's public webhook endpoint with the same body `B` and same `x-shopify-hmac-sha256: H`, but change `x-shopify-shop-domain` to `victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)` -> passes, because `to_signable_string` only checks `B` against `H`.
4. The handler is invoked with `WebhookMetadata.new(... shop: "victim.myshopify.com", body: parsed(B) ...)`, i.e. attacker-controlled body content attributed to the victim shop.

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
