### Title
Webhook shop identity spoofing via unauthenticated `shopify-shop-domain` header not covered by HMAC - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then reads the `shop` (tenant) identity from an HTTP header that is never included in the signed material. This breaks the binding "bytes verified == bytes the tenant identity is derived from", allowing an attacker who possesses one validly-signed webhook body (e.g., from their own shop, since HMAC uses the app's shared `client_secret`, not a per-shop secret) to replay it with a forged `shopify-shop-domain`/`x-shopify-shop-domain` header, causing the handler to process attacker-controlled data as if it originated from a different (victim) shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor, however, is read straight from the HTTP header without any cryptographic binding to the signature: [2](#0-1) 

`Registry.process` validates the HMAC using `Utils::HmacValidator.validate(request)`, which internally calls `request.to_signable_string` (body only) and `request.hmac`, and — critically — never checks `request.shop` against anything: [3](#0-2) 

`HmacValidator.validate` confirms the signature is computed only from `verifiable_query.to_signable_string` (the raw body) and the shared `Context.api_secret_key`: [4](#0-3) 

This is the same class of bug as the reported analog: a field that is acted upon (`shop`, used to build `WebhookMetadata` and dispatched to the app's handler as the tenant identity) is not covered by the authentication check (`hmac` over `raw_body` only). Since one `client_secret` is shared across every shop that installs the app, any body+HMAC pair that validates for one shop validates for all shops — the signature says "this body is authentic for this app," not "this body belongs to this shop." An attacker who controls (or has installed the app on) shop A can capture a validly-signed webhook body from shop A, then submit it directly to the app's webhook endpoint with the header rewritten to shop B's domain. `HmacValidator.validate` still returns `true` because it only checks the body bytes, and `Registry.process` forwards `shop: request.shop` (now `shop-b.myshopify.com`) to the handler.

### Impact Explanation
This allows cross-tenant data injection/spoofing: an attacker-controlled payload (e.g., a forged `orders/create`, `app/uninstalled`, `customers/data_request`, or `shop/redact` body) can be attributed to any shop the attacker chooses via the unauthenticated header, while still passing the library's HMAC check. Depending on how the host app uses `WebhookMetadata#shop` (e.g., looking up that shop's stored session/access token to act on its behalf, triggering GDPR redaction, or marking a shop as uninstalled), this can lead to cross-tenant state corruption or a mechanism for an attacker to falsely trigger privileged actions against a shop they do not own — a High-severity scope/identity boundary bypass carried entirely through the gem's own webhook verification API.

### Likelihood Explanation
Any developer using an app with multiple installed shops (the standard architecture for a Shopify public app) can obtain a legitimately signed body/HMAC pair from their own store's webhook deliveries at will (install the app on their own dev shop, trigger any webhook topic the app is subscribed to). No secret, token, or privileged access is required beyond having the app installed anywhere — which is the normal, unprivileged path for any merchant. Forging the header and replaying the request requires only basic HTTP tooling.

### Recommendation
Bind the shop identity to the signed payload instead of trusting the header verbatim: include the `shop-domain` (and ideally `webhook-id`/`topic`) header value in `to_signable_string`, or otherwise verify that the shop asserted by the header matches a shop actually known/authorized for this app (e.g., cross-check against a stored session for that shop) before dispatching to the handler in `Registry.process`.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and lets the app register for a webhook topic (e.g. `orders/create`).
2. Shopify delivers a webhook to the app with body `B` and header `X-Shopify-Hmac-Sha256: H` (computed as `HMAC-SHA256(client_secret, B)`) and `X-Shopify-Shop-Domain: attacker.myshopify.com`.
3. Attacker replays the exact same body `B` and `Hmac-Sha256: H` to the app's webhook endpoint but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `ShopifyAPI::Utils::HmacValidator.validate(request)` returns `true` because `to_signable_string` never included the shop header — validation in `lib/shopify_api/webhooks/request.rb:35-38` and `lib/shopify_api/utils/hmac_validator.rb:12-31`.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) invokes the app's handler with `shop: "victim.myshopify.com"` and the attacker-authored body, even though the payload never actually originated from `victim.myshopify.com`.

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
