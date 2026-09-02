### Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, while the `shop` (tenant) attribute that is handed to application handlers is read from an HTTP header that is never included in the signed data. Any party capable of triggering an outbound webhook for *any* shop (including a shop they themselves own/control) can capture a validly-signed body+HMAC pair and re-deliver it to the app's webhook endpoint with the `shopify-shop-domain` header swapped to any target shop, causing the library to hand the application a `WebhookMetadata` object that misattributes the event to a victim tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

but `shop` is read independently from the `shopify-shop-domain`/`x-shopify-shop-domain` header and is never mixed into the signable string: [2](#0-1) 

`Registry.process` verifies authenticity purely via `Utils::HmacValidator.validate(request)`, i.e. the HMAC-over-body check, and then forwards `request.shop` straight into the handler without any additional binding: [3](#0-2) 

`HmacValidator.validate`/`validate_signature` compute the signature only from `verifiable_query.to_signable_string` (the body) against `Context.api_secret_key`: [4](#0-3) 

This is exactly the identity-binding failure the reported analog describes: a field that is *acted on* (the `shop` used to attribute/route the webhook event to a specific merchant tenant) is not part of the data covered by the cryptographic proof (the HMAC). The equality that should hold — `shop_bound_by_hmac == shop_delivered_to_handler` — does not hold; the library only guarantees `hmac(body) == received_hmac`, it never guarantees `hmac` covers `shop`.

### Impact Explanation
Any actor who can obtain one legitimately-signed webhook body (e.g., by installing the app on their own store and triggering any webhook topic they've registered) possesses a valid `(body, hmac)` pair signed with the app's `client_secret`/`api_secret_key`. By replaying that exact body/HMAC to the app's public webhook endpoint while substituting the `shopify-shop-domain` header for a different, victim shop domain, they cause `ShopifyAPI::Webhooks::Registry.process` to pass HMAC validation and invoke the registered handler with `WebhookMetadata` claiming `shop: <victim-shop>`. If the host application uses `data.shop` (as the documented usage pattern in `docs/usage/webhooks.md` implies) to look up per-tenant sessions/data or to key business logic (e.g., processing `shop/redact`, `customers/redact`, order/customer events) per tenant, this results in cross-tenant data confusion/injection — an unprivileged internet user forging events attributed to a shop they do not control.

### Likelihood Explanation
Exploitation only requires the attacker to control (or install the app on) any single shop to obtain one valid signed payload, and does not require access to the app's `api_secret_key`, a merchant access token, or any privileged credential — satisfying the "unprivileged internet user" bar. The webhook endpoint is a public, unauthenticated HTTP callback by design, and no part of the library's `process`/`HmacValidator` code path validates that the `shop` header is consistent with, or bound to, the signed body.

### Recommendation
Bind the `shop` (and ideally `topic`/`api-version`) header values into the signed string used for HMAC verification (e.g., construct `to_signable_string` from a canonical concatenation of the relevant headers plus body, matching how Shopify itself computes the signature if it includes shop), or otherwise cryptographically verify that the `shop` claimed in the header matches the tenant that generated the payload before handing `WebhookMetadata` to handlers.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and registers/triggers any webhook topic handled by the app.
2. Attacker captures the raw POST body and the `x-shopify-hmac-sha256` header of that request — this HMAC is valid because `HmacValidator.compute_signature` only signs the body (`lib/shopify_api/utils/hmac_validator.rb:33-40`, `lib/shopify_api/webhooks/request.rb:36-38`).
3. Attacker replays the exact same body and `x-shopify-hmac-sha256` header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:189-199`) calls `Utils::HmacValidator.validate(request)`, which succeeds because the body is unchanged; the handler is invoked with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)`, even though the payload never originated from, nor was signed on behalf of, that shop.

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
