### Title
Webhook shop-domain header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw request body only, while the `shop` (and `topic`) attributes consumed by the webhook handler are read directly from HTTP headers that are never included in the signed material. `Registry.process` validates the HMAC and then trusts `request.shop` unconditionally, so any bytes verified by the signature are not the same bytes the handler acts on for tenant attribution.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Whereas `Request#shop` (and `topic`) are pulled straight from headers that are outside the HMAC computation: [2](#0-1) 

`HmacValidator.validate` only checks `verifiable_query.hmac` against `compute_signature(verifiable_query.to_signable_string, secret)`, i.e. it authenticates the body bytes, not the header bytes: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately builds `WebhookMetadata` using the unauthenticated `request.shop` and `request.topic`, handing it to the app's registered handler: [4](#0-3) 

The identity binding that should hold is: `shop authenticated by HMAC == shop attributed to the webhook payload passed to the handler`. Because the `x-shopify-shop-domain` (and `x-shopify-topic`) header is not part of the signed content, this equality is not enforced — the signature only proves "this body was signed with our shared secret," not "this body belongs to shop X."

**Attack path:** A holder of a legitimately installed shop (Shop A) receives real, correctly-signed webhook deliveries from Shopify for Shop A. That HMAC/body pair is valid, secret-independent, and replayable. The attacker captures one such `(raw_body, hmac)` pair and replays it to the app's webhook endpoint, substituting the `X-Shopify-Shop-Domain` header with Shop B's domain (a different tenant they do not control). `HmacValidator.validate` still succeeds because it only checks the body against the shared secret — it has no way to detect the header was swapped. The app's handler then processes data it believes originates from Shop B, using `request.shop` for tenant lookup/attribution, resulting in cross-tenant data being written or actions taken against the wrong tenant's session/store record.

### Impact Explanation
This meets the Critical bar for "cross-tenant access": an unprivileged user who merely installs the app on their own shop can cause the shared webhook-processing code path to attribute an authenticated-looking payload to a shop they do not own, because the shop identity is never bound into the signature the gem verifies.

### Likelihood Explanation
Likelihood is moderate-to-high: obtaining a genuine `(body, hmac)` pair only requires installing the app once (a normal, unprivileged action), and replaying an HTTP request with a modified header is trivial. Exploitability further depends on the host application using `WebhookMetadata#shop` for tenant lookups without any secondary check — which is the intended, documented use of this field per `handler.handle(data: WebhookMetadata.new(topic:, shop:, ...))` in `Registry.process`.

### Recommendation
Include the shop domain (and topic) in the HMAC-signed material, or otherwise cryptographically bind the header values to the verified body (e.g., derive/validate `shop` from a signed claim rather than a raw header), so that `HmacValidator.validate` fails whenever the shop-domain header does not match the body/secret that produced the signature.

### Proof of Concept
1. Register a webhook handler that persists data keyed by `data.shop` (the documented usage pattern):
```ruby
ShopifyAPI::Webhooks::Registry.add_registration(topic: "orders/create", path: "path", delivery_method: :http, handler: MyHandler)
```
2. As the owner of a legitimately installed `shop-a.myshopify.com`, capture a real webhook delivery's raw body and its `X-Shopify-Hmac-Sha256` header value (both computed and signed for `shop-a` by Shopify).
3. Replay the exact same raw body and HMAC header to the app's webhook endpoint, but set:
```
X-Shopify-Shop-Domain: shop-b.myshopify.com
```
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only compares `HMAC(secret, raw_body)` — it succeeds because the body is unchanged.
5. `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))` is invoked with `shop == "shop-b.myshopify.com"`, even though Shopify never signed anything for `shop-b`. Any handler logic keyed on `data.shop` now acts on the wrong tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
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
