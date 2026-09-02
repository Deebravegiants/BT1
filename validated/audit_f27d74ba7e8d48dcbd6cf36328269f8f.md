### Title
Webhook shop-domain (tenant) identity is not covered by the HMAC signature, allowing tenant spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` verifies webhook authenticity using an HMAC that only signs the raw request body, while the `shop` (tenant identity), `topic`, and `webhook_id` are read from unauthenticated HTTP headers and passed straight through to the registered handler. This breaks the equality "bytes verified == bytes/fields used to establish tenant identity," letting an attacker forge which shop a webhook payload is attributed to.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` validates a webhook solely via `Utils::HmacValidator.validate(request)`: [1](#0-0) 

`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string`: [2](#0-1) 

For `Webhooks::Request`, `to_signable_string` returns only `@raw_body` — the shop domain, topic, and webhook id headers are excluded from the signed content: [3](#0-2) 

`request.shop` is derived purely from the `x-shopify-shop-domain`/`shopify-shop-domain` header, with no cryptographic binding to the HMAC: [4](#0-3) 

Once the HMAC check passes (because it only validates the body bytes), `Registry.process` forwards `request.shop` (and `request.topic`, `request.webhook_id`) directly into `WebhookMetadata`, which the host application's handler uses to identify which merchant/tenant the event belongs to: [1](#0-0) 

The equality that should hold is: `shop_identity_bound_by_hmac == shop_identity_used_by_handler`. Instead: the HMAC only binds `raw_body`, while the handler trusts `request.shop` from an unsigned header. An attacker who can obtain any single validly-signed webhook body+HMAC pair for their own tenant (trivial — install the app on a shop they control and trigger any webhook event) can replay that exact `raw_body`/HMAC pair while substituting the `x-shopify-shop-domain` (and `x-shopify-topic`/`x-shopify-webhook-id`) header to a victim shop's domain. The signature still validates because the header is not part of the signed content, so the forged request is accepted and dispatched to the handler labeled as belonging to the victim tenant.

### Impact Explanation
This is a cross-tenant identity confusion: an app built on this gem, following its documented API (`Registry.process` + `WebhookMetadata.shop`), will process attacker-controlled webhook bodies while believing they originated from a different (victim) shop. Depending on how the host app uses `WebhookMetadata.shop` (e.g., to look up which merchant's data/access token to update, or to trigger tenant-scoped side effects such as `shop/redact`, `customers/redact`, `customers/data_request` compliance actions), this can lead to cross-tenant data corruption or unauthorized actions being attributed to/executed against another merchant's tenant — satisfying the "cross-tenant access" criterion.

### Likelihood Explanation
Likelihood is high for any attacker who can install the app on their own Shopify development store (a normal, unprivileged action) — they can capture one legitimate webhook (`raw_body` + valid `x-shopify-hmac-sha256`) and simply relay it with a modified shop-domain header to the app's public webhook endpoint. No possession of the app's `client_secret`/`api_secret_key` or the victim's credentials is required, since the HMAC is still valid for the (unmodified) body under the attacker's own legitimately-signed request.

### Recommendation
Include the shop domain (and ideally topic/webhook id) as part of the HMAC-signed content, or independently verify that the `x-shopify-shop-domain` header corresponds to an already-known/registered shop for the session that installed the webhook, before trusting `request.shop` in `WebhookMetadata`. At minimum, document/enforce that `shop` must be cross-checked against the app's own shop/session store rather than trusted directly from `Webhooks::Request#shop`.

### Proof of Concept
1. Install the target app on an attacker-controlled dev shop `attacker.myshopify.com`; trigger any subscribed webhook topic (e.g. `orders/create`) to receive a body `B` and a valid `x-shopify-hmac-sha256: H` computed over `B` with the app's `client_secret`.
2. Replay an HTTP POST to the app's webhook endpoint with the same raw body `B` and header `x-shopify-hmac-sha256: H`, but set `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC(B, secret) == H` — this succeeds because `B` and `H` are unchanged. [5](#0-4) 
4. The handler receives `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: parsed_body(B), ...)`, causing the app to process attacker-supplied data as if it came from the victim tenant. [6](#0-5)

### Citations

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
