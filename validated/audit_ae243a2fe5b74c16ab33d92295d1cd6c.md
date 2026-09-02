## Title
Webhook Shop/Topic Identity Spoofing via Unsigned Headers - (`lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, then dispatches to the registered handler using the `shop` and `topic` values parsed from HTTP headers that are **not covered by that HMAC**. This breaks the identity binding `hmac_verified_content == trusted_shop/topic`: the signature proves the *body bytes* came from a Shopify app secret holder, but the `shop-domain` and `topic` headers used to route/attribute the event to a tenant are attacker-controllable and never checked against the signature.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` accessors are parsed directly from headers with no relation to the signed content: [2](#0-1) 

`HmacValidator.validate` computes the signature only over `to_signable_string` (i.e., `raw_body`) and compares it to the `hmac` header: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop` and `request.topic` to build the metadata handed to the app's handler, without any check that these header values are the ones the signature actually covers: [4](#0-3) 

Because the HMAC secret (`Context.api_secret_key`) is the app's client secret — shared across every shop that installs the app, not a per-shop secret — any merchant who has the app installed can legitimately receive one genuine `(raw_body, hmac)` pair from Shopify for their own shop. That merchant can then replay the exact same body and HMAC to the app's webhook endpoint while forging the `X-Shopify-Shop-Domain` and/or `X-Shopify-Topic` headers to any value. `HmacValidator.validate` will still pass (it only checks body bytes against the secret), and `Registry.process` will hand the handler a `WebhookMetadata` claiming the forged `shop`/`topic`, even though the body was never generated for that shop or topic.

### Impact Explanation
This is a cross-tenant identity-binding break: the equality the library implicitly assumes — `verified(raw_body) ⇒ trusted(shop_header, topic_header)` — does not hold. A host application that keys any per-tenant action (e.g., looking up/loading the session or store record for `data.shop`, deciding which webhook handler logic applies via `data.topic`) off of `WebhookMetadata#shop`/`#topic` can be tricked into processing an attacker-supplied event as if it belonged to another merchant, since only the HMAC-authenticated bytes (the JSON body) are guaranteed genuine, not the routing metadata. This matches the Critical "cross-tenant access" category: one tenant (a merchant/attacker who is an unprivileged party relative to other tenants of the same app) can attribute forged webhook events to a different shop.

### Likelihood Explanation
Exploitation requires only that the attacker be a legitimate but unprivileged user of the shared app — i.e., any merchant who installs the app and receives at least one real webhook delivery (trivial to obtain, since webhooks are delivered automatically on install/registration). No access to `api_secret_key`, access tokens, or privileged accounts is needed; the attacker only replays intercepted-by-themselves, legitimately-received traffic with forged headers to the app's own public webhook endpoint.

### Recommendation
Include the identity fields that the handler will trust (`shop-domain`, `topic`, and ideally `webhook_id`) in the signed/verified content, or otherwise cryptographically bind them to the payload before dispatch — e.g., verify that the JSON body's declared shop/resource ownership matches the header-derived `shop`, or require the host application to independently confirm the `shop` against a known, previously-established session/store record before trusting `WebhookMetadata` for any tenant-scoped action. At minimum, document prominently that `Request#shop`/`#topic` are unauthenticated header values and must not be used as a sole tenant-identity source.

### Proof of Concept
1. As a merchant, install the target app on `attacker-shop.myshopify.com` and register for a webhook topic (e.g., `orders/create`).
2. Capture a genuine delivery: raw body `B` and header `X-Shopify-Hmac-Sha256: H` (valid because `HMAC-SHA256(app_secret, B) == H`).
3. Replay a POST to the app's webhook endpoint with the same body `B` and header `H`, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and/or a different `X-Shopify-Topic`).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes the HMAC over `B` — it succeeds because `B` and `H` are unchanged.
5. `Registry.process` dispatches `handler.handle(data: WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: parsed_body, ...))`, causing the host app to process attacker-controlled data as though it originated from `victim-shop.myshopify.com`. [4](#0-3) [5](#0-4)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
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
