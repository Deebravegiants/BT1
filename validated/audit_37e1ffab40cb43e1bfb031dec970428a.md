## Analog Finding

### Title
Webhook shop/topic/id headers are trusted without being covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the shop domain, topic, webhook id, and API version consumed by `ShopifyAPI::Webhooks::Registry.process` are read straight from unauthenticated HTTP headers. Any party that can obtain one genuinely-signed `(body, hmac)` pair — e.g. by installing the app on their own store — can replay that exact body to the app's webhook endpoint while rewriting the shop/topic headers to impersonate a different tenant, because nothing binds those header values to the signature.

### Finding Description
`Utils::HmacValidator.validate` verifies the HMAC by computing it over `verifiable_query.to_signable_string` and comparing it to the supplied `hmac` value: [1](#0-0) 

For webhooks, `to_signable_string` returns only the raw request body — none of the Shopify headers are included: [2](#0-1) 

Yet `shop`, `topic`, `webhook_id`, and `api_version` are all pulled directly from headers with no cryptographic tie to the signature: [3](#0-2) 

`Registry.process` validates only the HMAC over the body, then immediately builds and dispatches `WebhookMetadata` using the unauthenticated header values: [4](#0-3) 

`WebhookMetadata.shop` is a plain `String` field with no additional verification, and app handlers are expected to treat it as the authenticated origin shop: [5](#0-4) 

This is the same bug class as the report: an operation (dispatching webhook data attributed to a specific shop) is carried out based on a field (`shop-domain`/`topic`/`webhook-id` header) that is not part of what the safety/authenticity check (`HmacValidator`) actually covers. By contrast, the gem's own OAuth `AuthQuery` does this correctly — `shop` is explicitly included inside `to_signable_string` and thus is bound to the HMAC: [6](#0-5) 

The broken identity binding as an equality: the gem implicitly assumes `hmac_valid(raw_body) == shop_header_is_authentic`, but the actual invariant enforced is only `hmac_valid(raw_body)`; `shop`, `topic`, and `webhook_id` are read from bytes that were never covered by the signature, so `verified_bytes != header_bytes_acted_on`.

### Impact Explanation
Because every shop that installs an app shares the same `client_secret` (i.e. `Context.api_secret_key`), a webhook body that Shopify signs for the attacker's own store produces a valid HMAC that is not shop-specific. An attacker who owns/controls a shop that has installed the target app can capture a legitimately-signed `(raw_body, hmac)` pair from their own webhook deliveries, then replay it to the app's webhook endpoint with the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) header rewritten to name a victim shop. `Registry.process` will accept the HMAC (it only checks the body) and hand the handler a `WebhookMetadata` claiming to originate from the victim tenant. Any app logic keyed off `data.shop` (e.g. looking up/mutating the victim's stored session, triggering shop-scoped side effects, or writing audit data under the victim's identity) is corrupted — this is a cross-tenant integrity/confusion issue arising directly from this gem's webhook verification design.

### Likelihood Explanation
Exploitation requires only an ordinary/attacker-controlled shop installation of the vulnerable app (no privileged account, no leaked secrets, no TLS interception) and the ability to send an HTTP request with attacker-chosen headers to the app's public webhook endpoint — both are within reach of an unprivileged internet user as defined by the rules. The gem provides no documented requirement for apps to independently corroborate the `shop` header against anything else, so any app following the documented webhook-processing pattern in `docs/usage/webhooks.md` inherits this exposure.

### Recommendation
Include the identity-relevant headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) inside the signable content used by `HmacValidator`, or otherwise cryptographically bind them to the verified payload (e.g., by having `Request#to_signable_string` canonically embed these header values alongside the raw body before computing/verifying the digest), so that a mismatch between the signed body and any of these header values causes validation to fail.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`.
2. Attacker triggers a webhook event (e.g. `orders/create`) on their own shop and captures the raw POST: body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(client_secret, B)`.
3. Attacker sends a new HTTP request to the app's webhook endpoint with the same body `B` and same `H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only hashes `@raw_body` (`B`) — validation succeeds because `B` and `H` are unchanged.
5. `Registry.process` builds `WebhookMetadata.new(... shop: request.shop ...)` with `shop == "victim-shop.myshopify.com"` and invokes the app's handler, which now processes attacker-controlled data under the victim's identity.

### Citations

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
