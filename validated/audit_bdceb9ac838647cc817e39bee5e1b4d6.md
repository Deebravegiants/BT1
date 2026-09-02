### Title
Webhook `shop` (and `topic`/`webhook_id`) identity is taken from unauthenticated headers that are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC that `Utils::HmacValidator.validate` checks in `Webhooks::Registry.process` binds *only* the body bytes to the app's `api_secret_key`. The `shop`, `topic`, and `webhook_id` values that identify *which tenant and event* the payload belongs to are read straight from HTTP headers that are never included in the signed string, then handed unchecked to the app's webhook handler as the tenant key.

### Finding Description
`ShopifyAPI::Webhooks::Request` exposes: [1](#0-0) 

Note that `hmac` is computed by Shopify over the raw body, `to_signable_string` returns `@raw_body` only, while `shop`, `topic`, and `webhook_id` are pulled from `shopify_header(...)`. None of these three identity fields are part of the signable string.

`Registry.process` validates the HMAC of the body and then immediately trusts these header-derived fields to build the tenant-scoped data object passed to the handler: [2](#0-1) 

Because `HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb#L26-L31`) only recomputes the signature over `to_signable_string` (the body), the equality that is actually being checked is:
`HMAC(body, api_secret_key) == received_hmac`

but the equality the application *needs* — `shop header == shop that produced this signed body` — is never checked anywhere in the gem. `request.shop` is passed straight through to `WebhookMetadata.new(... shop: request.shop ...)` with no cryptographic binding to the HMAC-verified body.

### Impact Explanation
This breaks the binding between "bytes verified" and "bytes/headers acted on." Anyone who owns or controls an app installation (even a free/dev install on a shop they legitimately own) receives real webhook deliveries at their own public endpoint containing a valid `(raw_body, x-shopify-hmac-sha256)` pair signed with the app's `api_secret_key`. Nothing prevents replaying that exact `(body, hmac)` pair back to the same endpoint while substituting an arbitrary `x-shopify-shop-domain` header (and/or `x-shopify-topic`/`x-shopify-webhook-id`). `HmacValidator.validate` will still pass (body unchanged), and `Registry.process` will hand the (attacker-chosen) `shop` value straight to the handler alongside the original signed body. Any host application that uses `WebhookMetadata#shop` to key tenant data (the intended and expected use per the gem's design) will process another tenant's identifier together with attacker-replayable content — a cross-tenant data confusion/corruption primitive achievable without ever possessing the app's `client_secret`.

### Likelihood Explanation
Medium: the attacker needs at least one legitimate `(body, hmac)` pair, which is trivially obtainable by installing the target app on any shop they control (a normal, unprivileged action) and observing the webhook POST their own server receives. No secret material or privileged account is required to mount the header-substitution replay against the same public webhook endpoint.

### Recommendation
Bind the tenant/topic identity into the verified material instead of trusting unauthenticated headers:
- Either include `shop`, `topic`, and `webhook_id` in the value that `to_signable_string` returns (requires coordinating with Shopify's signing scheme, which currently only signs the body), or
- At minimum, have `Webhooks::Registry.process` cross-check `request.shop` against an out-of-band trusted source (e.g., the registration/session the request is associated with) before dispatching to the handler, and document to consumers that `WebhookMetadata#shop` must never be trusted as the sole tenant key without an additional binding check.

### Proof of Concept
1. Install the target app normally on `attacker-shop.myshopify.com`; Shopify delivers a legitimate webhook to the app's public endpoint:
   - Headers: `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: customers/update`, `x-shopify-hmac-sha256: <valid-hmac-of-body>`
   - Body: attacker-controlled JSON (attacker can trigger arbitrary customer/order updates on their own shop to control the body content).
2. Attacker resends the identical raw body and `x-shopify-hmac-sha256` value to the same webhook endpoint, but changes `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request#hmac`/`#to_signable_string` only look at the body, so:
   ```ruby
   ShopifyAPI::Webhooks::Registry.process(request) # HMAC check passes
   ```
4. `Registry.process` calls `handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: attacker_body, ...))`, causing the host app to process attacker-supplied data tagged as `victim-shop`'s tenant. [1](#0-0) [2](#0-1) [3](#0-2)

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
