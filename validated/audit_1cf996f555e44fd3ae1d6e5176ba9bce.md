### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing tenant spoofing in `Registry.process` - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, but exposes `shop` (the `shop-domain` header) as a trusted, unauthenticated identity field that `Registry.process` passes straight to the app's webhook handler.

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `HmacValidator.validate` recomputes the HMAC purely from that signable string and compares it to the `hmac-sha256` header [2](#0-1) . The `shop` value, however, is read from a separate, independent header (`shop-domain`) that is never included in the signed payload [3](#0-2) .

`Registry.process` validates the HMAC and then unconditionally trusts `request.shop` as the tenant identity passed to the handler: `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))` [4](#0-3) .

This breaks the intended identity binding: `HMAC(raw_body, client_secret) == received_hmac` should imply `shop-domain == the shop that actually sent this exact body`, but because `shop-domain` is excluded from the signable string, an attacker who can produce (or replay/relay) a validly-signed body for one shop can pair it with an arbitrary `shop-domain` header value, and the library will report it as authentic data for a different, attacker-chosen shop. In other words, `hmac_verified_shop == parsed_shop` does not hold; only `hmac_verified_body == parsed_body` holds.

### Impact Explanation
Downstream host applications rely on this gem's `WebhookMetadata#shop` to route data to the correct tenant record (as this is the documented purpose of the field, per `webhook_id`/`shop`/`topic` fields returned in `WebhookMetadata`). If an app trusts `shop` from `WebhookMetadata` (as the library's own interface encourages, since it is presented as an authenticated field alongside the topic and body that *are* HMAC-protected), an attacker able to influence the `shop-domain` header on an inbound webhook call (e.g., a body reused from one legitimate webhook but delivered/proxied with a different `shop-domain` header, or a man-in-the-middle-free scenario where the header is attacker-controllable at the HTTP layer in front of the app) could cause cross-tenant data to be attributed to the wrong shop. This matches the "cross-tenant access" class of impact.

### Likelihood Explanation
Exploitability depends on whether the `shop-domain` header can be manipulated independently of the signed body reaching the app (e.g., through a component in front of the Rails/Rack app that lets a caller set arbitrary headers, or a request-smuggling/relay scenario). Genuine Shopify-originated webhook deliveries always send matching body and shop values, so under normal, direct-to-origin conditions this is not directly triggerable by "any HTTP client on the internet" absent such a header-injection vector. This is a legitimate root-cause design flaw in the gem (missing an identity binding on a field the report class targets), but requires an additional condition (header spoofing/relay) to be fully weaponized, so likelihood is Medium.

### Recommendation
Include `shop-domain` (and other identity-bearing headers such as `topic`, `webhook-id`, `api-version`) inside `to_signable_string`, or otherwise bind these header values into the HMAC computation, so that a successfully-verified HMAC also guarantees the shop, topic, and other metadata are authentic and were not substituted after Shopify computed the signature.

### Proof of Concept
1. Capture (or otherwise obtain) a legitimately Shopify-signed webhook request: raw body `B`, `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(client_secret, B)`.
2. Deliver a request to the app's webhook endpoint with the same body `B` and the same signature `H`, but with `x-shopify-shop-domain` set to a different shop (`victim-shop.myshopify.com` while the body was actually for `attacker-shop.myshopify.com`, or vice versa).
3. `ShopifyAPI::Utils::HmacValidator.validate(request)` returns `true` because it only checks `HMAC(B) == H` [5](#0-4) .
4. `Registry.process` calls the handler with `shop: request.shop` set to the attacker-chosen value [6](#0-5) , causing the host app to process/store the body under the wrong tenant.

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
