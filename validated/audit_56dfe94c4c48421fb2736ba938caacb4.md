Based on the codebase analysis, there is a legitimate analog to the reported bug class.

### Title
Webhook shop/topic/webhook-id identity headers are not covered by the HMAC signature, allowing cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` signs and verifies only the raw request body via HMAC, while the `shop`, `topic`, `webhook_id`, and `api_version` values are read directly from unauthenticated HTTP headers and passed on trust to the registered webhook handler.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`, and `HmacValidator.validate_signature` computes/verifies the HMAC exclusively over that signable string: [1](#0-0) [2](#0-1) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are extracted directly from headers with no cryptographic binding to the signed body: [3](#0-2) 

`Registry.process` validates the HMAC (over the body only) and then unconditionally trusts `request.shop`, `request.topic`, and `request.webhook_id` when constructing the metadata handed to the app's webhook handler: [4](#0-3) 

This breaks the intended binding: `HMAC(body, api_secret_key) == received_hmac` should imply `(shop, topic, body)` all originate from the same authenticated Shopify delivery for that shop, but the equality only actually proves `body == body`. `shop` is never part of the signed material.

### Impact Explanation
Because `api_secret_key` is shared across all shops that install the app (it is not per-tenant), any merchant who installs the app can legitimately receive a webhook delivery for their own store — capturing a valid `(raw_body, hmac)` pair signed with the app's single shared secret. They can then replay this exact body/HMAC pair against the app's webhook endpoint while substituting the `x-shopify-shop-domain` (and optionally `x-shopify-topic`/`x-shopify-webhook-id`) headers to point at a victim shop. Since the HMAC never covered these headers, the signature remains valid, and `Registry.process` will pass `shop: <victim-shop>` to the app's handler along with attacker-chosen body content — a cross-tenant data injection into the victim shop's processing pipeline.

### Likelihood Explanation
Any user capable of installing the app on their own (attacker-controlled) shop — an unprivileged action available to any internet user with a Shopify Partner/dev store — can obtain a valid signed payload and replay it with forged identity headers against the app's public webhook endpoint. No access token, `api_secret_key`, or privileged account is required.

### Recommendation
Include the identity-relevant headers (`shop`, `topic`, `webhook_id`, `api_version`) in the signed/verified material, or otherwise cryptographically bind them to the HMAC-covered body (e.g., verify that `shop` matches a session/shop record independently established via OAuth before trusting it for routing/attribution), rather than relying solely on body-only HMAC verification plus unauthenticated headers.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and triggers a webhook delivery, capturing the raw POST body and the `x-shopify-hmac-sha256` header value (both computed with the app's shared `api_secret_key`).
2. Attacker resends the exact same body and `x-shopify-hmac-sha256` header to the app's webhook endpoint, but changes `x-shopify-shop-domain` to `victim.myshopify.com` (and optionally `x-shopify-topic`/`x-shopify-webhook-id`).
3. `HmacValidator.validate` succeeds because it only checks the body against the HMAC (`Request#to_signable_string` at `lib/shopify_api/webhooks/request.rb:35-38`).
4. `Registry.process` at `lib/shopify_api/webhooks/registry.rb:188-200` invokes the app's handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: <attacker-controlled>, ...)`, causing the app to process attacker-controlled data as if it came from the victim shop.

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
