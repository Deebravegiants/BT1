### Title
Webhook HMAC does not bind `shop-domain` or `topic` headers, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, while `#shop` and `#topic` are read from unauthenticated HTTP headers that are never included in the signed payload. `Utils::HmacValidator.validate` verifies the HMAC solely against `to_signable_string` (the body), so any request whose body+HMAC pair is valid for *some* shop will validate successfully regardless of what `shop-domain`/`topic` headers accompany it. This breaks the binding `hmac_signed_bytes == bytes_acted_on`, exactly the bug class described in the report (a field acted on — `shop`, `topic` — not covered by the integrity check).

### Finding Description
`Request#hmac` and `Request#to_signable_string` are defined as: [1](#0-0) 

`shop` and `topic` are pulled straight from headers with no cryptographic binding to the body: [2](#0-1) 

`Registry.process` validates only via `HmacValidator.validate(request)`, which internally calls `compute_signature(verifiable_query.to_signable_string, secret)` and compares it to `request.hmac` — i.e., it verifies the raw body bytes, not the shop/topic headers: [3](#0-2) [4](#0-3) 

Once the HMAC check passes, `request.shop` and `request.topic` are trusted and forwarded verbatim into `WebhookMetadata`, which is handed to the app's webhook handler: [5](#0-4) 

Because the identity binding actually enforced is `HMAC(body) == received_hmac`, but the binding *relied upon* by the handler is `(shop, topic, body)` all originating from the same authentic delivery, an attacker who controls one legitimate shop (any free/dev store — a normal unprivileged internet user with respect to the merchant app) can capture one of their own genuine webhook deliveries (valid `raw_body` + valid `hmac`) and resend it to the same app's webhook endpoint with the `X-Shopify-Shop-Domain` and/or `X-Shopify-Topic` headers rewritten to a victim shop/topic. The HMAC still validates because it only covers `raw_body`, so the handler executes believing the data belongs to the victim tenant.

### Impact Explanation
This meets the Critical bar for **cross-tenant access**: an attacker-controlled shop can cause the app to process webhook data under another shop's identity, since `shop` is trusted as an identity key for the resulting handler logic without being covered by the signature that is supposed to authenticate the sender.

### Likelihood Explanation
Any developer can install a Shopify app trial on their own store to legitimately receive real, correctly-signed webhooks (valid body + HMAC), then replay that request to the app's public webhook endpoint with modified `shop-domain`/`topic` headers. No access token, `client_secret`, or privileged access is required — this is achievable purely from data the attacker legitimately received as an ordinary merchant.

### Recommendation
Include `shop` (and ideally `topic`) in the signed/verified material, or independently verify that `request.shop` corresponds to a shop session/registration the app expects for that specific webhook subscription before trusting it in `to_signable_string`/`HmacValidator.validate`. At minimum, document that host applications must not use header-derived `shop`/`topic` as an authorization boundary without cross-checking against their own webhook registration records, and consider deriving `shop` from the signed body payload when the topic schema includes it.

### Proof of Concept
1. Install the target app as a normal merchant on `attacker-shop.myshopify.com`; trigger any subscribed webhook topic (e.g., `orders/create`) to receive a genuine webhook POST with a correctly computed `X-Shopify-Hmac-Sha256` header for the JSON body.
2. Capture the raw request: headers (`X-Shopify-Topic`, `X-Shopify-Hmac-Sha256`, `X-Shopify-Shop-Domain`, `X-Shopify-Webhook-Id`, `X-Shopify-Api-Version`) and raw body.
3. Replay the exact same body and `X-Shopify-Hmac-Sha256` value to the app's webhook endpoint, but change `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com` (and/or `X-Shopify-Topic` to another registered topic).
4. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `Registry.process` calls `HmacValidator.validate(request)`, which only recomputes HMAC over `raw_body` — validation succeeds.
5. The registered handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: <forged>, body: <attacker's own data>, ...)`, causing the app to attribute attacker-controlled data to the victim tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
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
