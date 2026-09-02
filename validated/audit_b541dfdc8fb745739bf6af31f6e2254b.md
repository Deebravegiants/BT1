### Title
Webhook `shop`/`topic` identity fields are trusted from unauthenticated headers while only the raw body is HMAC-verified, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates only the HMAC of the raw request body via `Utils::HmacValidator.validate(request)`, but the tenant-identifying fields `shop`, `topic`, `api_version`, and `webhook_id` that are passed to the app's handler are read directly from HTTP headers, which are **not** part of the HMAC-signed content. This breaks the identity binding `hmac_verified_bytes == bytes_the_handler_trusts_for_tenant_identity`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `api_version`, and `webhook_id` accessors instead read straight from caller-supplied headers with no cryptographic binding to the HMAC: [2](#0-1) [3](#0-2) 

`Registry.process` validates the HMAC of the request (i.e., of `@raw_body` only) and then immediately constructs `WebhookMetadata` using `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` taken from those unverified headers: [4](#0-3) 

`HmacValidator.validate` only ever computes/compares a signature over `verifiable_query.to_signable_string`, which for `Webhooks::Request` is the raw body — the shop domain is never part of what's signed: [5](#0-4) 

The gem's own documentation asserts that `Registry.process` "will verify the request did indeed come from Shopify" as a whole, and instructs the handler to treat `data.shop` as the authenticated tenant identity (`data.shop`, "The shop domain of the webhook"):

```
docs/usage/webhooks.md:125  "This will verify the request did indeed come from Shopify..."
docs/usage/webhooks.md:14   "`shop`, `String` - The shop domain of the webhook"
```

The `WebhookMetadata` struct exposes `shop` as a plain, trusted field to the handler with no further indication it is unauthenticated: [6](#0-5) 

**Identity binding broken (as an equality):**
`hmac_signed_content (raw_body)` ≠ `tenant_identity_used_by_handler (shop header, topic header, webhook_id header)`

Before attacker action: a genuine Shopify webhook for Shop A has `raw_body_A` (HMAC-valid) delivered with headers `shop=A, topic=T, webhook_id=W`.
After attacker action: an unprivileged holder of app credentials for Shop A (any merchant who installs the multi-tenant app — an "unprivileged internet user" relative to other tenants) captures/replays that same valid `raw_body_A` + HMAC to the app's public webhook endpoint, but substitutes `x-shopify-shop-domain: B` (a victim shop) in the request headers. Since the HMAC only proves the *body* bytes were signed by the shared `api_secret_key`, and the same `api_secret_key` is used for every shop of a multi-tenant app, the forged request passes `HmacValidator.validate` and `Registry.process` dispatches `WebhookMetadata.new(shop: "B", ...)` to the handler — a cross-tenant event injected into shop B's context despite never being sent by Shopify for shop B.

### Impact Explanation
This satisfies the Critical bucket "cross-tenant access": an attacker who is a legitimate installer of the app for their own shop (no special privilege, no access token or secret needed beyond what they already have as a normal merchant/tenant) can inject webhook events attributed to an arbitrary victim shop domain into the host application's webhook-processing pipeline, since the gem provides no mechanism verifying that the `shop` header is bound to the signed payload. Downstream host applications that key session/data lookups off `data.shop` (as the documented usage pattern in `docs/usage/webhooks.md` explicitly recommends: `perform_later(topic: data.topic, shop_domain: data.shop, ...)`) will process/act on this forged event as if it belongs to the victim tenant.

### Likelihood Explanation
Likelihood is bounded by the need to obtain at least one validly-signed body/HMAC pair, which any installed merchant automatically receives for their own store's real webhook traffic (e.g., `app/uninstalled`, generic topics with largely fixed/predictable JSON shape). No secret material, TLS interception, or privileged access is required — only normal use of the app as an installed merchant plus the ability to POST to the app's public webhook endpoint with attacker-controlled headers.

### Recommendation
- Include the `shop` (and ideally `topic`/`webhook_id`) values in the HMAC-signed content, or otherwise cryptographically bind the header-derived tenant identity to the verified payload before constructing `WebhookMetadata`.
- At minimum, update documentation to explicitly state that `Registry.process` only authenticates the body, not the `shop`/`topic`/`webhook_id` headers, and that host applications must independently verify the `shop` header corresponds to a shop that is actually registered/subscribed for that specific webhook (e.g., cross-check against the app's own webhook subscription records) before trusting `data.shop`.

### Proof of Concept
1. As shop A, install the multi-tenant app and let Shopify deliver a real webhook (e.g., `app/uninstalled`) — capture `raw_body` and the `x-shopify-hmac-sha256` header (both valid, signed by the shared `api_secret_key`).
2. Replay the exact same `raw_body` and HMAC header to the app's webhook endpoint, but set `x-shopify-shop-domain: B.myshopify.com` (any other tenant shop) and, if desired, a different `x-shopify-topic`/`x-shopify-webhook-id`.
3. `ShopifyAPI::Webhooks::Request.new` parses these headers into `request.shop == "B.myshopify.com"`.
4. `ShopifyAPI::Webhooks::Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which only checks `OpenSSL::HMAC.hexdigest(..., request.to_signable_string)` (i.e., raw body) — this passes since the body/HMAC pair is genuinely valid.
5. The handler is invoked with `WebhookMetadata.new(shop: "B.myshopify.com", ...)`, and any host logic keyed on `data.shop` now operates on forged data attributed to shop B. [7](#0-6) [8](#0-7)

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

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
