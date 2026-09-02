### Title
Webhook Shop Domain Spoofing via HMAC Not Covering Header Fields - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies a webhook's authenticity by checking an HMAC that covers only the raw request body, while the `shop` (and `topic`, `webhook_id`, `api_version`) values used to identify the tenant are taken directly from unauthenticated HTTP headers. An attacker who can obtain any one validly-signed webhook body (e.g., by installing the app on their own shop and receiving a legitimate webhook, since the HMAC secret — `api_secret_key` — is shared across all shops that install the app) can replay that body with a forged `shop-domain` header pointing at a victim shop. The signature check still passes because the header is never part of the signed payload.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are read straight from HTTP headers with no cryptographic binding to the body or to the HMAC: [2](#0-1) 

`Registry.process` validates only the HMAC of the body, then immediately trusts `request.shop` (and other header fields) to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

The `HmacValidator.validate` call computes `HMAC(api_secret_key, to_signable_string)`, i.e. `HMAC(api_secret_key, raw_body)` — the shop domain is never part of the signed material: [4](#0-3) 

Because `api_secret_key` is a single per-app secret shared across every shop that installs the app (not a per-shop secret), any merchant who installs the app is able to observe a legitimately-signed `(body, hmac)` pair for their own shop's webhook traffic. Since the `shop-domain` header is not covered by that signature, the same `(body, hmac)` pair remains valid when replayed with a different `x-shopify-shop-domain` (or legacy `x-shopify-shop-domain`) header value pointing at an arbitrary victim shop. The equality the code effectively (and incorrectly) asserts is: `hmac_valid(body) == shop_domain_header_is_authentic`, when in fact the header carries no cryptographic proof at all — it breaks the "shop authenticated vs. shop trusted by the host application" identity binding.

### Impact Explanation
This crosses the tenant boundary: an attacker-controlled shop can cause the host application to process a webhook payload as though it originated from a different, victim shop, since `WebhookMetadata#shop` (built entirely from the untrusted header) is what applications use to key their per-shop business logic. This matches "Critical - cross-tenant access."

### Likelihood Explanation
Any developer/merchant who installs a public app can capture a validly-signed webhook body for their own shop and replay it with an arbitrary `shop-domain` header value against the app's public webhook endpoint. No access token, `client_secret`, or privileged account is required — only ordinary use of the app as an installing merchant plus the ability to send an HTTP request to the app's exposed webhook route.

### Recommendation
Include the shop domain (and ideally topic/webhook id) as part of the HMAC-signed material, or otherwise cryptographically bind the header-derived `shop` value to the verified payload before constructing `WebhookMetadata`. At minimum, document that `request.shop` is unauthenticated and must not be trusted for cross-tenant authorization decisions without additional verification (e.g., confirming the shop against a known session/access-token record before acting on webhook data).

### Proof of Concept
1. Install the app on attacker-owned shop `attacker.myshopify.com`; trigger any webhook topic subscribed by the app (e.g. `orders/create`). Capture the raw POST body `B` and the resulting `x-shopify-hmac-sha256` header value `H` sent by Shopify (valid because `H = HMAC_SHA256(api_secret_key, B)`).
2. Send a forged HTTP request to the app's webhook endpoint with the same body `B` and header `H`, but with `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC_SHA256(api_secret_key, B)` and matches `H` — validation passes (`lib/shopify_api/webhooks/registry.rb:190`, `lib/shopify_api/utils/hmac_validator.rb:27-31`).
4. The handler is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed(B), ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`), causing the host application to process attacker-supplied data attributed to `victim.myshopify.com`.

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
