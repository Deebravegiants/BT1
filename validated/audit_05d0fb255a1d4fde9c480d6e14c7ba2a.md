### Title
Webhook shop/topic identity is not bound to the HMAC, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `HmacValidator.validate` verifies the HMAC exclusively against that body [1](#0-0) [2](#0-1) . The `shop`, `topic`, and `webhook_id` values that `Registry.process` uses to dispatch and tag the event are read straight from unauthenticated HTTP headers and are never included in the signed material [3](#0-2) [4](#0-3) .

### Finding Description
The identity binding that should hold is:

`shop bound in the HMAC == shop the app attributes the webhook event to`

Here it does not hold. `Registry.process` only checks `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (i.e. `@raw_body` only) and compares it to the `hmac` header value using `OpenSSL.secure_compare` [4](#0-3) [5](#0-4) . The `shop-domain`, `topic`, `webhook-id`, and `api-version` headers used to build `WebhookMetadata` (which the host app's handler treats as the authoritative tenant/topic identity) are parsed from `@headers` but are outside `to_signable_string`, so none of them are covered by the signature [6](#0-5) [7](#0-6) .

Because `api_secret_key` is a single, app-wide secret shared across all shops that install the app (the same secret is used to compute every shop's webhook HMAC, as seen in `Oauth.validate_auth_callback`'s use of `Context.api_secret_key` and in the webhook tests), any merchant that installs the app on their own store can obtain a body+HMAC pair that is valid for the shared secret [8](#0-7) . Since the header fields are excluded from the signed content, that same (body, hmac) pair remains valid no matter what `shop-domain`, `topic`, or `webhook-id` header values accompany it when replayed directly to the app's webhook endpoint.

### Impact Explanation
An attacker who controls a shop with the app installed can:
1. Trigger a webhook event on their own store to receive a body and its correctly computed `x-shopify-hmac-sha256` value from Shopify.
2. Replay that exact `(raw_body, hmac)` pair directly to the app's webhook receiver endpoint, substituting `x-shopify-shop-domain` with a victim shop's domain (and/or `x-shopify-topic`/`x-shopify-webhook-id`).
3. `HmacValidator.validate` still succeeds because it only checks the body, and `Registry.process` dispatches the forged `WebhookMetadata.new(shop: <victim shop>, ...)` to the registered handler [9](#0-8) .

Any host application that trusts `WebhookMetadata#shop` as the tenant key for storage, provisioning, or mandatory-webhook (GDPR) processing will attribute attacker-controlled data to a shop the attacker does not own — a cross-tenant data-integrity/confusion issue reachable purely through this gem's webhook verification path.

### Likelihood Explanation
Likelihood is high for any developer building on this library's public webhook API: they are told to call `Registry.process(request)` and trust the resulting `shop`/`topic` in `WebhookMetadata`, with no indication in the API surface that these values are unauthenticated. No secret material beyond installing the app on an attacker-owned shop is required to obtain a valid signature.

### Recommendation
Bind the tenant/topic identity into the signed material, e.g. include `shop-domain`, `topic`, and `webhook-id` header values (not just the raw body) in `to_signable_string`, or have `HmacValidator` separately validate that the `shop-domain` header matches a shop the caller expects/has a stored session for before dispatching to a handler. At minimum, document prominently that `WebhookMetadata#shop`/`#topic` are unauthenticated and must be cross-checked by the host app against a known/installed shop list before being trusted.

### Proof of Concept
```ruby
# Attacker's own shop receives a genuine webhook delivery from Shopify:
#   body:  '{"id":1,"note":"legit order on attacker shop"}'
#   headers: { "x-shopify-hmac-sha256" => "<valid HMAC for body>",
#              "x-shopify-shop-domain" => "attacker-shop.myshopify.com",
#              "x-shopify-topic" => "orders/create" }

# Attacker replays the identical body+hmac to the app's webhook endpoint,
# only changing the shop header:
forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => captured_hmac,          # unchanged, still valid for the body
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # not covered by HMAC
  "x-shopify-webhook-id" => "any-id",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: captured_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate succeeds (body unchanged);
#    handler.handle receives WebhookMetadata(shop: "victim-shop.myshopify.com", ...)
```

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L16-38)
```ruby
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```

**File:** test/webhooks/registry_test.rb (L16-20)
```ruby
        hmac = OpenSSL::HMAC.digest(
          OpenSSL::Digest.new("sha256"),
          ShopifyAPI::Context.api_secret_key,
          "{}",
        )
```
