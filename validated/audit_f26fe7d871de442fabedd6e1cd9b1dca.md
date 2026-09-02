Found it. The `Webhooks::Request#shop` value is read directly from the `X-Shopify-Shop-Domain` HTTP header, which is **not** part of the HMAC-signed payload, yet `Registry#process` trusts this header value as the tenant identity for dispatching webhook data to handlers.### Title
Webhook tenant identity (`shop`) is taken from an unauthenticated HTTP header, not from the HMAC-signed payload - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#shop` reads the tenant identifier straight from the `X-Shopify-Shop-Domain` HTTP header, while `Utils::HmacValidator.validate` only verifies the HMAC over the raw request body (`to_signable_string` returns `@raw_body`). The `shop` field is never covered by the signature check, yet `Registry.process` forwards this unauthenticated value to every webhook handler as the trusted tenant identity.

### Finding Description
`Webhooks::Request` includes `Utils::VerifiableQuery` and exposes `hmac` and `to_signable_string`: [1](#0-0) 

`hmac` is derived from the `X-Shopify-Hmac-Sha256` header and `to_signable_string` returns only `@raw_body` — the JSON body bytes. `shop` (line 20-23) is read from the `shop-domain` header, which is completely separate from `@raw_body` and thus **outside** the HMAC signature scope: [2](#0-1) 

`Utils::HmacValidator.validate` computes the signature purely over `to_signable_string` (the body) and compares it against the `hmac` header: [3](#0-2) 

`Registry.process` validates only this body HMAC, then immediately trusts `request.shop` as the tenant identity passed into the app's webhook handler via `WebhookMetadata`: [4](#0-3) [5](#0-4) 

The identity binding broken here is:
`shop authenticated (bytes covered by HMAC) != shop consumed by the handler (X-Shopify-Shop-Domain header, unauthenticated)`

Since the HMAC only proves that *some* legitimate Shopify-originated body with a given content was sent for *some* shop that installed the app (an attacker who has ever received one legitimate webhook delivery, e.g. by installing the app on their own shop, can capture a valid `(raw_body, hmac)` pair), the `shop-domain` header can be freely swapped to any other shop's domain when replaying that captured, still-HMAC-valid body to the app's webhook endpoint. `Registry.process` will still consider the payload authentic (since only the body+hmac pairing is checked) and will pass the attacker-chosen `shop` value straight to the handler as `WebhookMetadata.shop`.

### Impact Explanation
An app that (as documented) relies on `WebhookMetadata.shop` from this gem's `Registry.process` to determine which merchant/tenant's data store to write into can be tricked into attributing a captured, replayed webhook body to an arbitrary victim shop domain, since the gem itself never binds the `shop` field to the HMAC-signed content. This is a cross-tenant identity confusion: data or side effects intended for shop A's webhook can be attributed to shop B purely by changing an unauthenticated header, without needing the app's `client_secret`. This qualifies as cross-tenant access under the Critical impact criteria, since the mismatch is rooted entirely in this gem's own `Webhooks::Request`/`Registry` implementation rather than host-application misuse.

### Likelihood Explanation
The likelihood is Medium: exploitation requires the attacker to first obtain at least one legitimate `(raw_body, hmac)` pair — trivially achievable by installing the target app on their own shop (an ordinary unprivileged action for any Shopify merchant/developer) and capturing the webhook delivery. No `api_secret_key`, access token, or privileged access is required; only the ability to receive a normal HTTP webhook and replay it with a modified `X-Shopify-Shop-Domain` header to the app's exposed webhook endpoint.

### Recommendation
Bind the `shop` (and ideally `topic`) claim into the HMAC-signed content that `Webhooks::Request#to_signable_string` returns, or independently re-verify that the `shop-domain` header matches an app-side expectation (e.g., cross-check against the shop that actually owns the `webhook_id`/subscription) before trusting it in `Registry.process`. At minimum, document prominently that `WebhookMetadata.shop` is unauthenticated and must not be used by host applications as a trusted tenant key without additional verification.

### Proof of Concept
1. Attacker installs the target Shopify app on their own shop `attacker-shop.myshopify.com` and triggers a webhook (e.g. `orders/create`) — Shopify sends a POST with header `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Hmac-Sha256: <valid-hmac-of-body>`, and the JSON body.
2. Attacker captures the raw body and the valid HMAC header.
3. Attacker replays the exact same raw body and HMAC header to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks the (unchanged) body against the (unchanged) HMAC — `to_signable_string` never includes the `shop-domain` header. [6](#0-5) 
5. `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))` is invoked with `shop: "victim-shop.myshopify.com"`, even though the payload actually originated for `attacker-shop.myshopify.com`, letting the attacker inject attacker-controlled data under a victim shop's identity in any app logic keyed on `WebhookMetadata.shop`.

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
