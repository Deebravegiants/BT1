### Title
Webhook `shop-domain` and `topic` headers are trusted for shop attribution and handler routing without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates the webhook HMAC over the raw request body only, then uses the unauthenticated `x-shopify-shop-domain` and `x-shopify-topic` headers to attribute the event to a shop and to select which handler processes the payload. Since these headers are not part of the signed material, an attacker who obtains any single valid `(body, hmac)` pair can replay it with a different `shop-domain` or `topic` header and have the app process the data as if it came from a different shop or a different event type.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`ShopifyAPI::Utils::HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string`, i.e. over the raw body alone, and compares it to the `hmac-sha256` header: [2](#0-1) 

`Registry.process` gates on this body-only HMAC check, but then reads `request.topic` and `request.shop` — both taken directly from unauthenticated headers via `shopify_header` — to route the message to a handler and to populate `WebhookMetadata.shop`: [3](#0-2) [4](#0-3) 

The identity binding that should hold is: `shop header == shop bound inside the HMAC-covered content` and `topic header == topic bound inside the HMAC-covered content`. In this implementation neither holds — the HMAC only proves "this body was produced with the app secret at some point," not "for this shop" or "for this topic." Since the header values are attacker-mutable while the signature stays valid (HMAC is computed only over the body), any party capable of sending an HTTP POST to the app's public webhook endpoint (i.e., any unprivileged internet user), armed with one previously-observed valid `(body, hmac)` pair for the app's secret, can substitute an arbitrary `shop-domain` header to attribute the event to a different merchant/tenant, or substitute the `topic` header to have the body dispatched to a different (registered) handler than the one it was actually signed for.

This directly matches the bug-class pattern called out in the rules: "a field acted on but not covered by the HMAC."

### Impact Explanation
This breaks the shop/tenant identity binding for webhook processing: a handler can be invoked with `WebhookMetadata#shop` set to a shop that never actually produced that payload, allowing cross-tenant data confusion inside the host application (e.g., an app that persists webhook data keyed by `shop` could have another merchant's inventory/order/customer data attributed to a victim shop, or vice versa). It can also cause topic confusion, letting a captured payload from one webhook topic be dispatched to a handler intended for a completely different topic, in violation of the app's assumed processing contract. This falls under the "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires the attacker to already possess one legitimate `(raw_body, hmac)` pair produced with the app's real secret — the attacker cannot forge the HMAC without the secret. However, once such a pair is available (e.g. captured from network logs, a shared/leaked webhook payload, a webhook the attacker's own store received, or any endpoint that echoes/log the payload), no privileged credentials are needed to replay it against the public webhook endpoint with modified `shop-domain`/`topic` headers — this is a plain unauthenticated HTTP POST. Likelihood is therefore moderate: it depends on obtaining one valid signed body, but the replay itself requires no authentication or elevated access.

### Recommendation
Include the shop domain and topic (and any other fields you plan to trust for routing/attribution) inside the HMAC-covered signable content, or otherwise cryptographically bind them to the body (e.g., verify the shop/topic against Shopify-issued webhook metadata retrieved via an authenticated API call, not solely from headers). At minimum, `Request#to_signable_string` should incorporate `shop`, `topic`, and `webhook_id` so that `HmacValidator.validate` fails if any of those are tampered with independently of the body.

### Proof of Concept
1. Register handlers for two topics, e.g. `orders/create` (real merchant data) and `app/uninstalled` (destructive action) via `ShopifyAPI::Webhooks::Registry.add_registration`.
2. Capture (or otherwise legitimately receive) one valid webhook delivery for topic A: raw body `B` and its accompanying `x-shopify-hmac-sha256` header value `H`, valid for the app's secret.
3. Send a new HTTP POST to the app's webhook endpoint with the same body `B` and same `x-shopify-hmac-sha256: H`, but set `x-shopify-shop-domain: victim-shop.myshopify.com` and/or `x-shopify-topic: app/uninstalled`.
4. `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` succeeds because it only checks `B` against `H`.
5. `Registry.process` in `lib/shopify_api/webhooks/registry.rb` looks up the handler for the attacker-chosen topic and invokes it with `shop: "victim-shop.myshopify.com"`, causing the host app to process body `B` as if it belongs to `victim-shop` and/or under a topic it was never actually signed for.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
