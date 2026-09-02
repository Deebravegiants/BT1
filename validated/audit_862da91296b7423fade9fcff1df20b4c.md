### Title
Webhook shop/topic headers trusted for tenant routing without HMAC coverage - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` and `ShopifyAPI::Webhooks::Registry.process` validate a webhook delivery solely by checking the HMAC over the raw request body [1](#0-0) , while the `shop`, `topic`, `api_version`, and `webhook_id` fields that are handed to the application's handler are read directly from HTTP headers and are never included in the HMAC-signed content [2](#0-1) . This breaks the identity binding: `hmac_valid(raw_body) == true` is treated as proof that `(shop, topic)` are also authentic, but the equality that should hold — `hmac_covers(shop, topic, raw_body) == true` — never actually holds.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body` [3](#0-2) , and `HmacValidator.validate` computes/compares the signature exclusively against that signable string [4](#0-3) . Meanwhile, `Request#shop`, `#topic`, `#api_version`, and `#webhook_id` are parsed straight out of the `x-shopify-*`/`shopify-*` headers with no cryptographic tie to the body that was actually signed [5](#0-4) . `Registry.process` then forwards these header-derived values, including `shop`, directly into `WebhookMetadata` passed to the app's handler after only confirming the body HMAC [1](#0-0) .

Because the HMAC only binds the body, any raw body/HMAC pair genuinely produced by Shopify for one tenant's webhook (e.g., an attacker's own shop, which received a real webhook after installing the app) can be replayed to the app's webhook endpoint with a modified `shopify-shop-domain` header claiming to be a different shop, and the modified `shopify-topic` header claiming a different event type — the HMAC check still succeeds because it never covered those headers. This is analogous to the report's root cause of "a check that is bypassed because the constraint doesn't actually cover the field being acted upon" — here the constrained field is `raw_body`, but the field that gets acted upon by the host application (tenant identity via `shop`) is not covered at all.

### Impact Explanation
If the host application (following the gem's documented `WebhookMetadata`/handler pattern) uses `data.shop` to select which tenant's session/data the webhook payload should be applied to, an attacker who legitimately installed the app on their own store can forge webhook deliveries that appear to originate from — and get attributed to — a different merchant's shop, achieving cross-tenant data injection/confusion using only a genuinely-signed body they possess. This matches the "cross-tenant access" Critical impact category, since the shop identity binding used for tenant attribution is not actually protected by the signature the gem verifies.

### Likelihood Explanation
Exploitation requires an actor who has installed the app on at least one shop (to receive at least one genuinely HMAC-signed webhook body) and can then send arbitrary HTTP requests to the app's public webhook endpoint with modified headers — both are available to an ordinary, unprivileged internet user/merchant, with no need for `api_secret_key`, access tokens, or any other credential. Likelihood is Medium-to-High depending on whether the host application relies on `data.shop`/`data.topic` for authorization, which is exactly the field the gem's own `Registry.process` forwards after validation.

### Recommendation
Include the security-relevant headers (`shop`, `topic`, `webhook_id`, `api_version`) in the HMAC-covered signable string, or otherwise cryptographically bind them to the payload (e.g., have `Request#to_signable_string` canonicalize `headers + body`), so that `HmacValidator.validate` fails if any of these header fields are altered post-signing. Document clearly that `WebhookMetadata#shop`/`#topic` must not be trusted for tenant routing unless bound this way, or update the verification to enforce the binding inside the gem.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and receives a genuine webhook delivery with body `raw_body` and header `x-shopify-hmac-sha256: <valid_hmac_for_raw_body>` computed by Shopify with the app's real `api_secret_key`.
2. Attacker replays this exact `raw_body` and `x-shopify-hmac-sha256` value to the app's public webhook endpoint, but changes `x-shopify-shop-domain` to `victim-shop.myshopify.com` (and optionally `x-shopify-topic`).
3. `Webhooks::Request.new` parses headers, and `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only re-computes/compares the HMAC of `raw_body` [6](#0-5) [7](#0-6) .
4. The app's handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` [8](#0-7)  even though the signature never validated that shop value, allowing the attacker-controlled body to be processed under the victim's tenant identity.

### Citations

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
