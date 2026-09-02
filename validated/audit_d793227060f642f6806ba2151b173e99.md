The docs at `docs/usage/webhooks.md:125` explicitly state that `ShopifyAPI::Webhooks::Registry.process` "will verify the request did indeed come from Shopify" — establishing that this gem's documented API promises the caller that a validated request's metadata, including `shop`, can be trusted.

### Title
Webhook shop/topic/webhook_id identity spoofing due to HMAC covering only the raw body, not headers - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook exclusively via `Utils::HmacValidator.validate(request)`, and that validator only signs/verifies `request.to_signable_string`, which is defined as the raw HTTP body. The `shop`, `topic`, and `webhook_id` values consumed and handed to app handlers come from HTTP headers that are entirely outside the HMAC's coverage, breaking the equality `hmac_verified_bytes == identity_bytes_trusted`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Request#shop`, `#topic`, `#webhook_id` are read straight from HTTP headers with no cryptographic binding to the body or to the HMAC [2](#0-1) . `HmacValidator.validate` computes `OpenSSL::HMAC.hexdigest` over `verifiable_query.to_signable_string` (i.e., body only) and compares against the `hmac-sha256` header value [3](#0-2) . `Registry.process` treats a passing HMAC check as sufficient authentication of the whole request, then immediately trusts `request.shop`, `request.topic`, and `request.webhook_id` to build `WebhookMetadata` passed to the app's handler [4](#0-3) . The library's own documentation states that `process` "will verify the request did indeed come from Shopify," implying the whole `WebhookMetadata` (including `shop`) is trustworthy after this call.

Because the HMAC never covers the `shop-domain`, `topic`, or `webhook-id` headers, any body+HMAC pair legitimately delivered by Shopify to an attacker's own merchant endpoint (i.e., a webhook for a shop the attacker legitimately owns/controls, still signed with the target app's `client_secret` by Shopify) can be replayed by the attacker directly to the target app's public webhook endpoint with the `shop-domain` header rewritten to an arbitrary victim shop domain, and/or `topic`/`webhook-id` rewritten. The signature check still passes because it only re-verifies the body bytes, which are unchanged.

### Impact Explanation
This breaks the identity binding "bytes verified" (raw body signed with the app's `client_secret`) versus "bytes trusted for tenant identity" (`shop` header). It allows cross-tenant confusion: an app's webhook handler acts on data as if it originated from an arbitrary target shop when it actually originated from the attacker's own shop (or a forged topic), without requiring knowledge of `client_secret` or any credential belonging to the victim. Depending on the handler's logic (e.g., processing `shop/redact`, `customers/redact`, `orders/create`, uninstall handling keyed off `shop`), this can lead to unauthorized state changes attributed to a shop that never sent that event — a cross-tenant impact directly reachable through this gem's own webhook verification abstraction.

### Likelihood Explanation
The attacker only needs to control (or install the target app on) any shop to legitimately receive a real, validly-signed webhook delivery from Shopify for that app, then re-POST the identical body+HMAC to the same public endpoint with modified `shopify-shop-domain`/`shopify-topic`/`shopify-webhook-id` headers. No secret material, session, or elevated privileges are required beyond normal use of the app as any merchant, and the endpoint is public by design (webhook receivers are internet-reachable). This is a straightforward, unprivileged replay/header-rewrite attack.

### Recommendation
Bind `shop`, `topic`, and `webhook_id` into the HMAC-verified surface (e.g., require the receiving application to cross-check `shop` against the shop stored for the `webhook_id`/subscription it registered, or have `HmacValidator`/`Request#to_signable_string` incorporate the relevant headers into the signed payload verification), and document that `shop`/`topic` values are not currently authenticated by `Registry.process`'s HMAC check so integrators do not rely on them as an authenticity guarantee.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com`, subscribes/triggers a webhook (e.g., `orders/create`), and captures the resulting HTTP request Shopify sends to the app's webhook endpoint, including the real `x-shopify-hmac-sha256` header and raw body — both valid, since `Utils::HmacValidator.validate` only checks the body [5](#0-4) .
2. Attacker replays this exact `raw_body` and `hmac-sha256` header to the same public webhook endpoint, but changes `x-shopify-shop-domain` to `victim.myshopify.com` (and optionally `x-shopify-topic`/`x-shopify-webhook-id`).
3. `Registry.process` calls `HmacValidator.validate(request)` [6](#0-5) , which passes because the body is unmodified.
4. `Registry.process` builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` from the forged headers and invokes the handler [7](#0-6) , causing the app to act as though `victim.myshopify.com` sent this event.

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
