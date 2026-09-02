## Title
`Webhooks::Request#shop` (shop-domain header) is not covered by the HMAC signature, allowing cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
The webhook HMAC verification in this gem only authenticates the raw request body. The `shop` value that the registry hands to application webhook handlers — the field the host app uses to decide *which merchant's* data the webhook is about — comes from an HTTP header that is never included in the signed bytes. Since the same `api_secret_key` is shared across every shop that installs the app, any merchant who receives one genuine webhook can replay its body+signature while swapping the `shop-domain` header to point at a different, victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery`, and its `to_signable_string` returns only the raw HTTP body: [1](#0-0) 

The `shop` accessor, however, is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header, independent of the signed body: [2](#0-1) 

`Registry.process` validates the HMAC using `Utils::HmacValidator.validate(request)`, which calls `to_signable_string` (the body) — it never touches `request.shop` — and then forwards `request.shop` unmodified into the data passed to the app's handler: [3](#0-2) 

`HmacValidator.validate` itself only computes the signature over `verifiable_query.to_signable_string`: [4](#0-3) 

The identity binding that should hold is: `shop attested by HMAC == shop acted on by the handler`. Because the `shop-domain` header is excluded from `to_signable_string`, that equality does not hold — the HMAC only proves "this body was signed with the app's `api_secret_key`," not "this body originated from shop X." Since `api_secret_key` is one value shared by the app across *all* installing shops, any merchant who installs the app receives a genuine `(body, hmac)` pair for their own shop and can resend it to the app's webhook endpoint with an arbitrary `shopify-shop-domain` header. The signature still validates because the header plays no part in the computation, so `Registry.process` calls the handler with `WebhookMetadata.new(... shop: request.shop ...)` pointing at whatever shop domain the attacker chose.

### Impact Explanation
This breaks the tenant boundary the HMAC is supposed to enforce: any app that uses `request.shop`/`WebhookMetadata#shop` to key its lookups or updates (e.g., "update the record for `data.shop`") can be made to apply an attacker-controlled payload to another merchant's data, since the HMAC gives no assurance that the body actually belongs to the shop named in the header. This is cross-tenant access enabled purely by an unprivileged app-installing user replaying their own legitimately-signed webhook body under a spoofed shop identity.

### Likelihood Explanation
Any user who can install the app on their own store obtains at least one legitimately HMAC-signed webhook body (e.g., by triggering `orders/create` or any subscribed topic on their own shop). Replaying it with a modified `shopify-shop-domain` header to the app's public webhook endpoint requires no secret material and no privileged access — only a basic HTTP client.

### Recommendation
Bind the shop identity to the signature: include the `shop-domain` (and ideally `webhook-id`/`api-version`) in the bytes fed into `to_signable_string`, or otherwise cryptographically tie the shop claim to the body (e.g., derive/confirm the shop from a signed session/webhook-id lookup instead of trusting the header). At minimum, document and enforce that consuming applications must independently verify `data.shop` against a known, previously-registered shop for that webhook subscription rather than trusting the header value implied by the request.

### Proof of Concept
1. Install the target app on shop `attacker.myshopify.com`; trigger a subscribed webhook topic (e.g., `orders/create`) to receive a genuine request with body `B`, and header `x-shopify-hmac-sha256: H` valid for `HMAC(api_secret_key, B)`.
2. Resend the exact same request to the app's webhook endpoint, keeping body `B` and header `x-shopify-hmac-sha256: H` unchanged, but replace `x-shopify-shop-domain` with `victim.myshopify.com`.
3. `Utils::HmacValidator.validate` recomputes `HMAC(api_secret_key, B)` — matches `H`, so it passes — and `Registry.process` invokes the handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed(B), ...)`, i.e., attacker-controlled body attributed to the victim shop. [3](#0-2) [5](#0-4)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-43)
```ruby
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

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
