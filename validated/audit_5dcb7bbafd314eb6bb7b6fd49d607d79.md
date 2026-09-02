## Title
Webhook Shop-Domain and Metadata Headers Not Covered by HMAC Signature Enable Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop`, `topic`, `webhook_id`, and `api_version` values used by `ShopifyAPI::Webhooks::Registry.process` to route and attribute the webhook are taken from unauthenticated HTTP headers that are excluded from the signature.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0)  This is the string that `HmacValidator.validate` uses to recompute and compare the signature: [2](#0-1) 

However, `Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are all read directly from HTTP headers (`shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`, `shopify-api-version`), which are never included in `to_signable_string` and therefore never validated by the HMAC check: [3](#0-2) 

`Registry.process` validates the HMAC over the body only, then dispatches the handler using the unauthenticated `shop`, `topic`, and `webhook_id` values: [4](#0-3) 

The binding that is broken is: `shop authenticated by HMAC` ≠ `shop delivered to the handler`. Because the app's webhook secret (`Context.api_secret_key`) is shared across every shop that installs the app, any tenant that has installed the app can receive a legitimately-signed webhook body+HMAC pair for their own shop, then replay that exact `raw_body`+`hmac-sha256` pair to the app's webhook endpoint while substituting the `shopify-shop-domain` (and/or `shopify-topic`, `shopify-webhook-id`) header to name a different, victim shop. `Utils::HmacValidator.validate` will still pass because it only checks the body bytes, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the victim shop as the source: [5](#0-4) 

### Impact Explanation
This is a cross-tenant identity confusion: an attacker who controls one shop installation of the app can forge webhook deliveries that the app's webhook handler will attribute to any other shop the attacker names in the header, without needing that shop's credentials. If the host application's webhook handler uses `WebhookMetadata#shop` to look up/update per-tenant records (a common and expected usage pattern, e.g. updating that shop's order/product data), the attacker can inject or corrupt another merchant's data, or trigger shop-scoped side effects (e.g. billing, fulfillment, notification) under the wrong tenant.

### Likelihood Explanation
Exploitation requires the attacker to be an unprivileged user of the app on at least one shop (a normal, non-privileged prerequisite — anyone can install a public/dev app), and to send one crafted HTTP POST replaying a body+HMAC pair from their own webhook delivery with a modified shop/topic header. No secrets, tokens, or elevated access are required, and the gem itself performs no validation binding these headers to the signed content.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` (in addition to the raw body) in the signable payload used for HMAC verification in `Request#to_signable_string`, or otherwise cryptographically bind these header values to the signature so that the shop/topic used for dispatch cannot be altered independently of the signed content.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a genuine webhook (e.g. `orders/create`), receiving a valid `X-Shopify-Hmac-Sha256` signature for that request body.
2. Attacker replays the exact same raw body and `X-Shopify-Hmac-Sha256` header to the app's webhook endpoint, but changes `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com` (and optionally `X-Shopify-Topic`/`X-Shopify-Webhook-Id`).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because only the body bytes are checked: [6](#0-5) 
4. The registered handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` and processes attacker-controlled data as if it originated from the victim shop.

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
