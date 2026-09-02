Confirmed: `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are all read directly from unauthenticated HTTP headers with no cryptographic binding to the HMAC [2](#0-1) . `Registry.process` validates only the body HMAC and then forwards the header-derived `shop` value straight to the app's handler as the tenant identity [3](#0-2) .

### Title
Webhook shop-domain header is not covered by HMAC, enabling cross-tenant webhook spoofing via body replay - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signable string from the raw body only [1](#0-0) , but the tenant-identifying `shop` field consumed by `ShopifyAPI::Webhooks::Registry.process` and handed to the app's webhook handler is read from the `X-Shopify-Shop-Domain` HTTP header, which is completely outside the HMAC's coverage [4](#0-3) [3](#0-2) .

### Finding Description
`Utils::HmacValidator.validate` is generic: it recomputes the signature over whatever `to_signable_string` returns and compares it against the `hmac` field of the same object [5](#0-4) . For the OAuth callback (`Auth::Oauth::AuthQuery`), `to_signable_string` includes `shop` itself, so the shop identity is cryptographically bound to the signature [6](#0-5) . For `Webhooks::Request`, however, `to_signable_string` returns only `@raw_body` — the `shop`, `topic`, `webhook_id`, and `api_version` header values are never part of the signed material [1](#0-0) .

`Registry.process` treats a passing `HmacValidator.validate(request)` as proof of authenticity for the whole request, then immediately trusts `request.shop` (an unauthenticated header) as the tenant to route the event to: `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...))` [3](#0-2) .

The equality that should hold — "shop bytes verified by the HMAC" == "shop bytes acted upon by the handler" — is broken. Only the body bytes are verified; the shop field acted upon is taken from an independent, unsigned header. Any party capable of obtaining one genuine webhook delivery for their own shop (e.g., a legitimate merchant installing the app, which is an unprivileged action relative to any other tenant) can capture a raw body + valid HMAC pair and replay it to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header rewritten to point at a victim shop. `HmacValidator.validate` still succeeds because it only checks the (unchanged) body, and the forged shop header sails straight through to the application handler.

This mirrors the reported bug class: a verification step covers one representation of the data (raw body / NFT address+ID) while the code acts on a broader or different unverified field (shop header / ERC-1155 amount) that determines value or identity.

### Impact Explanation
This is a cross-tenant identity confusion at the gem's webhook-authenticity boundary: an attacker who controls their own shop's webhook stream can produce events that the host application will process as if they originated from a different, victim shop, since `WebhookMetadata.shop` (used by apps to key merchant records/data) is sourced from an unverified header. Depending on how the host app uses `shop` (e.g., looking up and mutating merchant records, redacting data, updating subscription state), this can lead to cross-tenant data corruption or disclosure — classified as Critical (cross-tenant access) per the impact taxonomy, since the gem's own `HmacValidator`/`Webhooks::Request` API is what is supposed to guarantee the webhook's shop attribution but does not.

### Likelihood Explanation
Exploitation requires only the ability to receive one legitimate webhook for an attacker-owned shop (trivial for anyone who installs, or has installed, the target app on any store) and the ability to send an arbitrary HTTP request to the app's public webhook endpoint with modified headers — no access to `api_secret_key`, access tokens, or the victim's credentials is needed, since the HMAC over the replayed body is unchanged and still validates.

### Recommendation
Bind `shop`, `topic`, and `webhook_id` into the HMAC-covered signable string (or otherwise cryptographically bind them to the verified payload) in `ShopifyAPI::Webhooks::Request#to_signable_string`, so `HmacValidator.validate` fails if any of these header values are altered relative to what Shopify actually signed.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and registers a webhook (e.g., `orders/create`).
2. Shopify delivers a webhook to the app with headers `X-Shopify-Shop-Domain: attacker.myshopify.com`, `X-Shopify-Hmac-Sha256: <hmac-of-body>`, and some JSON body `B`.
3. Attacker captures the raw body `B` and the valid `X-Shopify-Hmac-Sha256` value (computed by Shopify over `B` using the app's real secret, which the attacker never needs to know).
4. Attacker replays the exact same body `B` and HMAC header to the same app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
5. `Webhooks::Request.new` parses headers and `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `to_signable_string` (`= B`, unchanged) and matches the supplied HMAC header — validation passes [7](#0-6) .
6. `request.shop` returns `"victim.myshopify.com"` from the forged header [4](#0-3) , and this value is passed into `WebhookMetadata` and delivered to the app's handler as if it were an authentic event from the victim shop [8](#0-7) .

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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
