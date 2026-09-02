### Title
Webhook `shop` identity is not bound by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature only over the raw request body, while the `shop` value that is later trusted and forwarded to the app's webhook handler is read from an unauthenticated header. The binding `shop_used_by_handler == shop_covered_by_hmac` does not hold, so a request whose body+HMAC pair is valid for one shop can be replayed with an arbitrary `shop-domain`/`x-shopify-shop-domain` header and will still pass verification, letting an attacker attribute webhook data to a victim shop of their choosing.

### Finding Description
`Utils::HmacValidator.validate` verifies the HMAC using `verifiable_query.to_signable_string` as the signed payload: [1](#0-0) 

For webhooks, `to_signable_string` is defined to be only the raw HTTP body, and `shop` is a completely separate accessor read straight off request headers, never mixed into the signed string: [2](#0-1) 

`Registry.process` verifies the HMAC and then unconditionally trusts `request.shop` (and `request.topic`) to build the `WebhookMetadata` passed into the app's handler: [3](#0-2) 

Because the header carrying `shop` is never part of the signed bytes, the security check "HMAC is valid" says nothing about which shop the payload belongs to. Any unprivileged internet user who can obtain one valid `(raw_body, hmac)` pair — for example by installing the app on a shop they control and capturing a real webhook delivery — can resend that exact body/HMAC to the app's public webhook endpoint while substituting the `shop-domain` header with a victim shop's domain. `HmacValidator.validate` still succeeds (it only recomputes the HMAC over the unchanged body), and `Registry.process` forwards `WebhookMetadata` claiming the data belongs to the victim shop. The app's handler — which typically looks up the merchant's session/access token by `shop` — will act on attacker-supplied content believing it originates from the victim tenant.

This mirrors the reported bug class: a security check (`HMAC valid?`) is used as a proxy for a claim (`this data is authentically from shop X`) that it does not actually cover, because the field the app relies on (`shop`) is outside the range validated by the check, allowing the identity binding to be bypassed.

### Impact Explanation
This breaks the tenant boundary the gem's webhook verification is supposed to enforce: a handler can be invoked with attacker-chosen payload content while believing it is authoritative data from an arbitrary victim `shop`. Depending on how the host application's handler uses `shop` (e.g., to look up the merchant's session/access token and perform actions, write data, or trigger downstream side effects "on behalf of" that shop), this enables cross-tenant data injection/confusion — an unprivileged attacker forges events attributed to a shop they do not own and never authenticated as.

### Likelihood Explanation
Medium-High. The attacker only needs one legitimately-signed `(body, hmac)` pair, which is trivially obtainable by installing the app on their own store (a normal, unprivileged action) and capturing any resulting webhook delivery. No secret key, access token, or privileged access is required to then replay it with a forged `shop-domain` header against the same public endpoint.

### Recommendation
Include the shop domain (and ideally the topic) inside the HMAC-signed payload/signable string, or otherwise cryptographically bind the `shop` header value to the request signature, so verification fails if `shop` is swapped without also being able to recompute a matching signature. At minimum, document that `WebhookMetadata#shop` is not itself authenticated by the HMAC check and must not be trusted as a tenant identifier without additional verification by the host application.

### Proof of Concept
1. Install the target app on `attacker-shop.myshopify.com` and trigger any webhook subscribed by the app; capture the raw `raw_body` and the resulting `x-shopify-hmac-sha256` value — this is a valid `(body, hmac)` pair.
2. POST to the app's webhook endpoint reusing the exact same `raw_body` and `x-shopify-hmac-sha256`, but set `x-shopify-shop-domain: victim-shop.myshopify.com` and `x-shopify-topic` as desired.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (only `raw_body`) — [4](#0-3)  — and succeeds because the body was untouched.
4. `Registry.process` builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)` using the attacker-supplied `shop` header value and invokes the registered handler with it — [5](#0-4) , causing the app to process attacker-controlled data as if it belonged to `victim-shop.myshopify.com`.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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
