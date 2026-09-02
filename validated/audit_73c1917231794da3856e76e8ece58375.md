### Title
Webhook `shop` field is trusted from an unauthenticated header while HMAC only signs the raw body, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` extracts `shop` from the `X-Shopify-Shop-Domain` HTTP header, but the HMAC signature it validates only covers the raw request body. `Registry.process` trusts this header-derived `shop` value when dispatching to the tenant-scoped webhook handler, without any cryptographic binding between the signed bytes and the claimed shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read straight from an unauthenticated header, entirely independent of the signed payload: [2](#0-1) 

`Utils::HmacValidator.validate` only checks `verifiable_query.hmac` against `compute_signature(verifiable_query.to_signable_string, secret)`, i.e., it validates the body bytes against the shared app secret and never touches `shop`: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately dispatches to the handler using `request.shop` as the tenant identity, with no additional check that this header matches the shop that actually produced the signed body: [4](#0-3) 

The identity binding that should hold is: `shop the HMAC authenticates == shop acted upon by the handler`. Because the HMAC secret (`Context.api_secret_key`) is shared across every shop that has the app installed, and the signature covers only `raw_body`, any party capable of obtaining one valid `(raw_body, hmac)` pair for the app (e.g., a merchant who installs the app on their own store and can trigger webhook content they control, or who registers their own webhook subscription via the Admin API with `write_webhooks` scope to capture genuine Shopify-signed deliveries) can replay that exact body and HMAC to the app's public webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header. `HmacValidator.validate` still passes because it never inspects the header, and `Registry.process` hands the forged `shop` straight to the handler.

### Impact Explanation
This breaks the tenant boundary: an unprivileged merchant/app-installer can make the host application process a webhook as if it originated from a different shop that also uses the same app, since the shop identity is not part of what the HMAC authenticates. This is a cross-tenant access primitive — the attacker can drive tenant-scoped side effects (e.g., data updates, redact/GDPR flows, order/customer processing) tagged to a victim shop of their choosing, using content they fully control.

### Likelihood Explanation
Exploitation requires only that the attacker be a legitimate, unprivileged installer of the target app on a store they control, and the ability to send an HTTP POST to the app's known webhook endpoint with a captured/replayed `(raw_body, hmac)` pair and a forged shop-domain header — no access to `api_secret_key`, access tokens, or the target shop's credentials is needed. The `client_secret`/`api_secret_key` is shared across every shop that installs the app, so a valid signature obtained on one shop's traffic is valid for a forged shop-domain claim.

### Recommendation
Bind the shop identity into the value that is actually cryptographically verified. Options: include `shop` (and ideally `topic`/`webhook_id`) in the signable string used for webhook HMAC validation, or require the host application to independently confirm that the header-derived `shop` corresponds to a shop with a currently valid, stored session/access token before trusting `WebhookMetadata#shop` for any tenant-scoped action, and document this expectation clearly in `ShopifyAPI::Webhooks::Registry.process`.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (any unprivileged Shopify merchant can do this for a public app).
2. Attacker registers (or otherwise obtains) a genuine Shopify webhook delivery for an event they can trigger with attacker-controlled body content, capturing the raw POST body and the `X-Shopify-Hmac-Sha256` header Shopify computed with the app's shared secret.
3. Attacker replays the identical raw body and HMAC header to the app's real webhook endpoint (backed by `ShopifyAPI::Webhooks::Registry.process`), but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate(request)` returns `true` because it only checks `raw_body` against the shared secret — `lib/shopify_api/utils/hmac_validator.rb:12-31`.
5. `Registry.process` proceeds and calls the registered handler with `shop: "victim-shop.myshopify.com"` — `lib/shopify_api/webhooks/registry.rb:189-199` — even though that shop never produced this payload.

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
