This confirms the finding: the webhook `shop`, `topic`, and `webhook_id` values are read directly from HTTP headers and passed to the app's handler as trusted identifiers, while `ShopifyAPI::Utils::HmacValidator.validate` only authenticates the raw request body against the HMAC — it never binds the `shop-domain`, `topic`, or `webhook-id` headers into the signed content.

### Title
Webhook shop/topic/webhook-id identity not covered by HMAC, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw body, then trusts the `shop`, `topic`, and `webhook_id` values taken from unauthenticated HTTP headers when constructing the `WebhookMetadata` passed to the app's handler. Because the signature never binds these header values, a party who can obtain any one valid `(raw_body, hmac)` pair for the app's shared `api_secret_key` can replay it with a forged `shop-domain`/`topic` header and have the handler process it as if it came from a different shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `shop`, `topic`, `webhook_id`, `api_version` are read straight from attacker-suppliable headers with no relation to the signature [2](#0-1) .

`Utils::HmacValidator.validate` computes and compares the signature only over `verifiable_query.to_signable_string` (i.e. the raw body) [3](#0-2) . It never incorporates `shop`, `topic`, or `webhook_id`.

`Registry.process` relies exclusively on this HMAC check, then immediately builds `WebhookMetadata` from the unauthenticated header fields and dispatches it to the app's handler: [4](#0-3) .

Because Shopify signs webhooks with the app's single `api_secret_key`, shared across every merchant that installs the app, any merchant that installs the app (an "unprivileged" party from the app's perspective, requiring no special access) legitimately receives real `(raw_body, hmac)` pairs for their own shop. That merchant can replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) header with a victim shop's domain. `HmacValidator.validate` will still accept the request — it only checks that the body matches a signature produced with the shared secret, not that the signature is bound to the specific shop or topic claimed in the headers. The identity binding that should hold, `shop_that_signed_the_body == shop_the_handler_believes_sent_it`, is broken: the gem verifies "bytes of the body were signed by the app's secret" but the handler acts on "shop asserted by an unauthenticated header."

### Impact Explanation
This breaks tenant isolation (Critical - cross-tenant access category). A handler that uses `data.shop` to decide which merchant's records to create/update/delete (the exact usage pattern shown in this gem's own documentation, e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) can be tricked into attributing one shop's webhook payload to a different shop, corrupting data across tenants or triggering shop-scoped side effects (e.g. inventory sync, order creation, GDPR data erasure flows) for the wrong merchant. The severity depends on how much the host app trusts `data.shop`/`data.topic` without independent cross-checking, but the gem itself provides no protection and documents these fields as trustworthy webhook metadata.

### Likelihood Explanation
Any entity that can install the app as a normal merchant (a low bar, often self-service) receives legitimately signed webhook deliveries for their own store and thus obtains valid `(body, hmac)` pairs signed with the app's shared secret. Forging the `shop-domain`/`topic` headers on a replayed HTTP POST requires no cryptographic material, no access to `api_secret_key`, and no privileged account — only the ability to send an HTTP request to the app's public webhook callback URL, which by design is a public, unauthenticated endpoint.

### Recommendation
Bind the `shop`, `topic`, and `webhook_id` into the value that is verified, e.g. include them (along with the raw body) in the HMAC-signed content check, or independently verify that `request.shop` matches a shop known to have an active webhook subscription with the given `webhook_id`/topic (e.g., cross-check against the registry/database of registered webhooks and known active sessions) before dispatching to the handler. At minimum, document prominently that `data.shop`/`data.topic` are not cryptographically bound to the payload and must not be trusted for authorization decisions without additional verification.

### Proof of Concept
1. Install the target app on `attacker.myshopify.com` and provoke a real webhook (e.g. `orders/create`) to be delivered to the app's callback URL. Capture the raw body and the valid `x-shopify-hmac-sha256` value Shopify computed with the app's shared `api_secret_key`.
2. Replay an HTTP POST to the same callback URL with the identical raw body and `x-shopify-hmac-sha256` header, but set `x-shopify-shop-domain: victim-shop.myshopify.com` (and optionally a different `x-shopify-topic`/`x-shopify-webhook-id`).
3. `ShopifyAPI::Webhooks::Registry.process` computes `Utils::HmacValidator.validate(request)` [5](#0-4) , which passes because it only checks the body-derived signature.
4. The handler is invoked with `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)` where `shop` is `"victim-shop.myshopify.com"` even though the payload never originated from that shop, causing the app to act on the wrong tenant's behalf.

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
