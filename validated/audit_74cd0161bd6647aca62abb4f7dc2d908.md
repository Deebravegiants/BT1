This confirms the exploit path: `Registry.process` verifies HMAC only over the raw body via `to_signable_string` returning `@raw_body`, then passes `request.shop` — sourced from the unsigned `x-shopify-shop-domain` header — directly to the handler as the tenant identity.### Title
Webhook `shop` identity is taken from an unauthenticated header not covered by the HMAC signature - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies the webhook's HMAC signature, but the signed payload used for verification is only the raw request body. The `shop` value handed to the app's webhook handler is read from the `X-Shopify-Shop-Domain` HTTP header, which is never included in the HMAC-signed bytes. This breaks the identity binding `hmac_signed_bytes == data_acted_on`, allowing the shop-domain field to be substituted independently of the signature that is supposed to authenticate the whole request.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The shop tenant identity, however, is read from a header, not from the signed body: [2](#0-1) 

`Registry.process` validates the HMAC using `Utils::HmacValidator.validate(request)`, which calls `verifiable_query.to_signable_string` (the raw body only) and `verifiable_query.hmac` (derived from the `hmac-sha256` header), then immediately forwards `request.shop` — the unsigned header value — to the registered handler as the tenant identity: [3](#0-2) [4](#0-3) 

Because the HMAC is computed with `HMAC-SHA256(client_secret, raw_body)` only [5](#0-4) , an attacker who possesses one valid `(raw_body, hmac)` pair for the app (trivially obtainable by installing the app on a shop they control and capturing a legitimate webhook delivery to their own endpoint) can resend that exact body+HMAC to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header. `HmacValidator.validate` will still pass because it never inspects the header, yet `Registry.process` passes the attacker-chosen `shop` value straight to `handler.handle`, misattributing the webhook payload to a shop the attacker does not own.

### Impact Explanation
Any app built on this gem that uses the `shop` field from `Webhooks::Registry.process`/`WebhookMetadata` to select which merchant's data to update, delete, or act upon (a common and expected usage pattern for GDPR/mandatory webhooks such as `shop/redact`, `customers/redact`, `customers/data_request`, or ordinary business webhooks) can be tricked into performing actions against, or associating attacker-controlled payload content with, a different tenant than the one that actually sent the data. This is a cross-tenant identity-binding failure: the app trusts an unauthenticated field as if it were verified by the HMAC.

### Likelihood Explanation
Exploitation requires only:
1. Installing the target app on a shop the attacker controls (a normal, unprivileged action any Shopify user can do, not requiring `api_secret_key`, an access token, or social engineering), and
2. Capturing one webhook delivery (any topic) sent to the attacker's own endpoint, and
3. Replaying that body+HMAC to the same app's webhook endpoint with a forged `Shop-Domain` header value naming the victim shop.

No credentials, TLS interception, or leaked secrets are needed — the attacker legitimately receives a valid signature for their own shop and repurposes it. This is entirely reachable by an unprivileged internet user through the gem's own documented processing path (`Registry.process` → `handler.handle`).

### Recommendation
Bind the `shop` (and ideally `topic`, `api_version`, `webhook_id`) values into the data that is cryptographically verified, or at minimum cross-check the header-derived `shop`/`topic` against values embedded in the verified JSON body where Shopify includes them, before invoking the handler. At a minimum, document/enforce that `WebhookMetadata#shop` must not be trusted for authorization decisions unless corroborated by an out-of-band verified source (e.g., the session/shop the webhook was registered for), and consider validating that the `shop` header matches an expected/registered shop domain associated with the receiving endpoint.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` and enables a webhook topic (e.g. `orders/create`).
2. Shopify delivers a webhook to the app's endpoint with headers:
   - `X-Shopify-Hmac-Sha256: <valid HMAC of raw_body with app's client_secret>`
   - `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`
   - body: `{"id": 123, ...}`
3. Attacker captures this exact `raw_body` and `X-Shopify-Hmac-Sha256` value.
4. Attacker sends a new HTTP request to the same app's webhook endpoint, keeping `raw_body` and `X-Shopify-Hmac-Sha256` identical, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
5. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `raw_body` only and it matches → validation passes: [6](#0-5) 
6. `handler.handle` is invoked with `shop: "victim-shop.myshopify.com"` and the attacker's `body`, even though the signature never authenticated that shop value: [7](#0-6)

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
