## Title
Webhook shop/topic/webhook-id headers are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/utils/hmac_validator.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as fully authenticated once `Utils::HmacValidator.validate(request)` succeeds, and then forwards attacker-controllable header values (`shop`, `topic`, `webhook_id`, `api_version`) straight to the app's handler. However, the HMAC signature only ever covers the raw request body — never the `shop-domain`, `topic`, or `webhook-id` headers. This breaks the identity binding `shop authenticated == shop delivered to handler`, allowing a party who has captured one legitimately-signed webhook body to relabel it as belonging to a different, arbitrary shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

`HmacValidator.validate_signature` computes/verifies the HMAC exclusively over `verifiable_query.to_signable_string`: [2](#0-1) 

`Registry.process` gates entirely on this HMAC check, then immediately trusts `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` — all sourced straight from unauthenticated HTTP headers — to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

The `shop`, `topic`, and `webhook_id` accessors simply read headers with no cryptographic tie to the signed body: [4](#0-3) 

Because the signature never binds these headers, `hmac(body) == valid` says nothing about which shop, topic, or webhook the body actually belongs to. A user who legitimately receives one real webhook (e.g. by installing the public app on their own store) obtains a `(raw_body, x-shopify-hmac-sha256)` pair that remains valid for that body forever, for any header values they choose to attach. They can then submit that exact body/HMAC pair to the app's webhook endpoint while setting `x-shopify-shop-domain` to a victim shop's domain (and/or an arbitrary `topic`/`webhook-id`). `Registry.process` will accept it as valid and hand the handler a `WebhookMetadata` claiming the data came from the victim shop.

### Impact Explanation
Any app whose webhook handler uses `WebhookMetadata#shop` to key session/database lookups (the pattern shown in this gem's own docs, e.g. `ShopifyAPI::Webhooks::Registry.register_all(session: shop_session)` per-shop flows) can be made to apply attacker-supplied — but Shopify-signed — payloads to a different tenant's account/session. This is a cross-tenant data-integrity break: the gem's own "validated" webhook guarantees only the body's integrity, not the shop/topic identity that the API surface (`WebhookMetadata`) implies is trustworthy. This falls under the Critical "cross-tenant access" category, since a merchant of shop A can cause the app to process webhook content under shop B's identity.

### Likelihood Explanation
Exploitation requires no privileged credentials, no `api_secret_key`, and no access token — only the ability to install the target app on any shop (including a free development store) to receive one legitimate webhook, then replay it with a modified `shop-domain`/`topic`/`webhook-id` header to the app's public webhook endpoint. This is achievable by any unprivileged internet user who can become a merchant of some shop running the app.

### Recommendation
Bind the identity headers into the signable payload (e.g., include `shop`, `topic`, and `webhook_id` in the HMAC-covered string, or require the handler/registry to independently verify `request.shop` against the session/shop the body's `id`/resource actually belongs to before trusting it). At minimum, document prominently that `Registry.process`'s "validation" only covers body integrity, not header authenticity, so host apps do not rely on `WebhookMetadata#shop` as a trusted tenant identifier without additional verification.

### Proof of Concept
1. Install the vulnerable app on attacker-controlled shop `attacker.myshopify.com`; capture a real webhook delivery, e.g. `orders/create`, noting `raw_body` and header `x-shopify-hmac-sha256: <valid_hmac>`.
2. Since `HmacValidator` only signs `raw_body` (`lib/shopify_api/webhooks/request.rb:35-38`, `lib/shopify_api/utils/hmac_validator.rb:26-31`), the same `(raw_body, hmac)` pair remains valid regardless of other headers.
3. POST to the app's webhook endpoint with the captured `raw_body` and `x-shopify-hmac-sha256`, but set:
   ```
   x-shopify-shop-domain: victim-shop.myshopify.com
   x-shopify-topic: orders/create
   ```
4. `Registry.process` calls `Utils::HmacValidator.validate(request)` → `true` (body/HMAC match), then invokes the registered handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` (`lib/shopify_api/webhooks/registry.rb:188-200`), causing the app to process attacker data under the victim shop's identity.

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
