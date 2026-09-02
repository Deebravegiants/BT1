### Title
Webhook `shop-domain` field is trusted for tenant attribution but is not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook as authentic once `Utils::HmacValidator.validate(request)` succeeds, then forwards `request.shop` (read straight from the `x-shopify-shop-domain`/`shopify-shop-domain` header) to the app's handler as the tenant identifier. The HMAC, however, is computed only over the raw request body, so the `shop` field the handler trusts for tenant attribution is never bound to the signature that "authenticates" the request.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor is populated purely from an unauthenticated header, independent of the signed content: [2](#0-1) 

`HmacValidator.validate` recomputes the HMAC only over `to_signable_string` (i.e., the body) and compares it to the `hmac` header: [3](#0-2) 

`Registry.process` gates entirely on that body-only HMAC, then passes the unauthenticated `request.shop` value into `WebhookMetadata` given to the app's handler: [4](#0-3) 

The equality the code implicitly claims but never enforces is:
`shop authenticated (bytes covered by HMAC) == shop acted on (WebhookMetadata#shop used by the handler for tenant routing)`

Because `shop` is excluded from the signable string, any request with a body/HMAC pair that is valid for the app's secret (e.g., one derived from a webhook legitimately delivered to a shop the attacker controls, since an attacker can install the app on their own store and receive real, correctly-signed webhooks for arbitrary content they create) can be replayed with the `shop-domain` header rewritten to a victim shop's domain. `Registry.process` will still consider the request "verified" and will hand the handler a `WebhookMetadata` claiming to be from the victim shop.

### Impact Explanation
This breaks the tenant-identity binding the gem is documented to provide ("This will verify the request did indeed come from Shopify" — `docs/usage/webhooks.md` line 125), which downstream host applications rely on to route webhook data per-shop (e.g., updating the correct shop's local records, looking up the correct access token, or triggering shop-scoped side effects) based on `WebhookMetadata#shop`. An attacker able to obtain any one valid (body, hmac) pair for the target app — trivially available by installing the app on their own store and triggering a webhook with attacker-controlled body content — can spoof the `shop` attribution for that payload towards any other shop, since the shop is never part of what's cryptographically verified. This is a cross-tenant data confusion vector at the boundary the gem is meant to authenticate.

### Likelihood Explanation
Moderate-to-high for public apps: obtaining a valid signed webhook only requires installing the app on an attacker-owned store (a normal, unprivileged action for any public app), and then relaying that request with a modified header to the app's webhook endpoint. No access to `api_secret_key` or any privileged credential is required — the header is not part of the trust boundary the HMAC establishes, so it is directly attacker-controllable in the replay.

### Recommendation
Bind the shop identity into the value that is cryptographically verified rather than trusting an unauthenticated header for tenant attribution. Options: incorporate `shop-domain` (and other tenant-scoping headers such as `webhook-id`, `api-version`) into the HMAC-signable string used by `Utils::HmacValidator`, or require callers to independently cross-check `request.shop` against a shop already registered/expected for the given `webhook_id`/session before acting on the data in `Registry.process`.

### Proof of Concept
1. Install the target public app on an attacker-controlled shop `attacker.myshopify.com`.
2. Trigger a webhook (e.g., `orders/create`) with attacker-chosen body content; Shopify delivers a request with a valid `x-shopify-hmac-sha256` computed over that body using the app's real `api_secret_key`, and header `x-shopify-shop-domain: attacker.myshopify.com`.
3. Capture the `(raw_body, hmac_header)` pair.
4. Replay the same `raw_body`/`hmac` to the app's webhook endpoint, but with `x-shopify-shop-domain` rewritten to `victim.myshopify.com`.
5. `ShopifyAPI::Utils::HmacValidator.validate(request)` still succeeds because it only checks the body against the HMAC (`lib/shopify_api/utils/hmac_validator.rb` lines 12-31, `lib/shopify_api/webhooks/request.rb` lines 35-38), so `Registry.process` calls the handler with `WebhookMetadata(shop: "victim.myshopify.com", body: <attacker-controlled>, ...)`, causing the host application to act on attacker data under the victim shop's identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
