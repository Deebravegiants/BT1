### Title
Webhook shop/topic identity is not bound to the HMAC, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, while the `shop`, `topic`, `api-version`, and `webhook-id` fields are read directly from unauthenticated HTTP headers. `Webhooks::Registry.process` validates only the body's HMAC and then forwards the header-derived `shop` value straight to the handler, so the tenant identity attached to a webhook event is never actually covered by the signature.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

All other identity-bearing fields — `shop`, `topic`, `api_version`, `webhook_id` — are pulled unauthenticated straight from HTTP headers: [2](#0-1) 

`HmacValidator.validate` only checks that `hmac` matches a signature computed over `to_signable_string` (the raw body): [3](#0-2) 

`Registry.process` accepts the request once the body HMAC passes, then constructs `WebhookMetadata` using the *unauthenticated* `request.shop`, `request.topic`, `request.api_version`, and `request.webhook_id`, handing them to the app's handler as trusted values: [4](#0-3) 

This breaks the intended equality: `shop_bound_by_hmac == shop_used_by_handler`. In reality, `shop_bound_by_hmac` is undefined (the signature says nothing about the shop), while `shop_used_by_handler = request.shop` is taken verbatim from an attacker-controllable header. Anyone who can obtain one valid `(raw_body, hmac)` pair (e.g., an attacker who installs the app on their own shop and lets Shopify deliver them a legitimate webhook) can replay that same body/HMAC pair with the `x-shopify-shop-domain` header (and/or `x-shopify-topic`) changed to any victim shop or topic. `HmacValidator.validate` still passes because it only checks the body, and the handler is invoked believing the event originated from and pertains to the attacker-chosen shop.

### Impact Explanation
This is a cross-tenant identity-binding bypass: an unprivileged party who has legitimately received a single valid webhook (no `api_secret_key`, no access token needed) can forge webhook deliveries claimed to be for a different merchant/shop or a different topic, using the exact same signed body. Depending on how the host application's webhook handler uses `WebhookMetadata#shop`/`#topic` (e.g., to route data, revoke access, process orders, or trigger GDPR/mandatory-compliance workflows for "that shop"), this can lead to cross-tenant data confusion or actions being taken under the wrong shop's identity — matching the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Likelihood is high for any developer relying on the gem's documented webhook flow (`Webhooks::Registry.process` / `Webhooks::Request`) as the sole authentication mechanism for identifying the originating shop, since the gem's own `HmacValidator` and `Request` classes never bind `shop`/`topic` to the signature. No secret material, access tokens, or elevated access are required — only capture/possession of one legitimately delivered webhook body+HMAC pair (trivially obtainable by installing the app on an attacker-owned development store).

### Recommendation
Include the identity-bearing headers (`shop`, `topic`, `webhook_id`, `api_version`) in the signable content used for HMAC validation, or otherwise cryptographically bind them to the body signature, so that `Utils::HmacValidator.validate` fails if any of these header values are altered relative to what Shopify actually signed.

### Proof of Concept
1. Attacker installs the target app on their own development shop `attacker.myshopify.com` and receives a legitimate webhook delivery: body `B`, header `x-shopify-hmac-sha256: H` (valid per `HmacValidator`), `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker resends the same request to the app's webhook endpoint, keeping body `B` and `x-shopify-hmac-sha256: H` unchanged, but sets `x-shopify-shop-domain: victim.myshopify.com` (and/or a different `x-shopify-topic`).
3. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `Utils::HmacValidator.validate(request)` in `Registry.process` (lib/shopify_api/webhooks/registry.rb:190) still succeeds because it only recomputes the HMAC over `@raw_body`.
4. The registered handler is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)`, causing the host application to process/act on data as though it legitimately came from `victim.myshopify.com`.

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
