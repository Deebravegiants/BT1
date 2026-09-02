### Title
Webhook `shop`/`topic`/`webhook_id` headers are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw request body, and `ShopifyAPI::Webhooks::Registry.process` validates the HMAC solely over that body before trusting the `shop`, `topic`, `webhook_id` and `api_version` values taken from unauthenticated HTTP headers. Any caller that can produce (or replay) a body/HMAC pair valid for the app's shared secret can attach arbitrary `X-Shopify-Shop-Domain`/`X-Shopify-Topic` headers, and the gem will hand that forged identity straight to the host application's webhook handler as if it were verified.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` and defines: [1](#0-0) 

`to_signable_string` returns `@raw_body` only — none of the Shopify-provided headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) are part of the signed material.

`ShopifyAPI::Webhooks::Registry.process` calls the HMAC validator against this request and, once it passes, immediately builds the metadata handed to the app's handler from the *headers*, not from anything the HMAC actually covers: [2](#0-1) 

`request.shop`, `request.topic`, and `request.webhook_id` are all read straight from the HTTP headers: [3](#0-2) 

The HMAC is computed with `Context.api_secret_key`, which is the **same secret for every shop that installs the app** — it is not shop-specific: [4](#0-3) 

Because the signature binds only the body, and the body for many webhook topics does not embed the originating shop, a `(body, hmac)` pair that was legitimately generated for one shop remains a valid signature for that same body no matter which `shop-domain` header accompanies it. The library has no mechanism to bind the verified bytes to the shop/topic identity it reports to the handler — this is exactly the "bytes verified vs. bytes acted on" class of bug: the equality that should hold, `shop_authenticated_by_hmac == shop_delivered_to_handler`, does not, because `shop_authenticated_by_hmac` doesn't exist at all — only `body_authenticated_by_hmac` does.

### Impact Explanation
An attacker who is a legitimate (unprivileged) merchant installing the app on their own store shares the app's single `api_secret_key` with every other tenant. If they can obtain or construct any valid `(body, hmac)` pair (e.g. from a webhook delivered to their own shop, or from a topic whose body is static/predictable/attacker-controlled), they can POST it to the app's public webhook endpoint with a forged `X-Shopify-Shop-Domain` header naming a victim shop. `Registry.process` will validate the HMAC (it matches, since only the body is checked) and dispatch to the handler with `WebhookMetadata#shop` set to the attacker-chosen victim shop. Any host application that trusts `data.shop` to scope database writes, cache invalidation, entitlement checks, or downstream API calls using a stored session for that shop is exposed to cross-tenant data manipulation — the Critical-tier "cross-tenant access" impact.

### Likelihood Explanation
This requires only: (1) being an app-installing merchant (an ordinary, unprivileged action available to any internet user who installs the app), and (2) obtaining one valid signed body for any topic delivered to the app. No access to the app's `client_secret`, no TLS interception, and no privileged account are required. The likelihood is higher for topics whose payload doesn't vary by shop or is otherwise attacker-influenceable, but the fundamental design flaw — verifying bytes that are disjoint from the identity fields that are acted upon — exists for every topic.

### Recommendation
Bind the verified signature to the identity fields that the handler is going to trust. At minimum, include `shop`, `topic`, and `webhook_id` in the signable payload (mirroring how `AuthQuery#to_signable_string` includes `host` alongside `code`/`shop`/`state`/`timestamp`), or otherwise cryptographically bind the header values to the HMAC-verified body before constructing `WebhookMetadata`. Alternatively, require/verify a per-shop signing context so that a signature valid for shop A's body cannot be replayed while claiming to be shop B.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (normal, unprivileged onboarding flow).
2. Attacker triggers (or otherwise obtains) one legitimate webhook delivery for a topic whose body doesn't embed the shop identity, capturing `raw_body` and the corresponding `X-Shopify-Hmac-Sha256` value — both are valid for the app's single shared `api_secret_key`.
3. Attacker sends their own HTTP POST directly to the app's public webhook endpoint with the same `raw_body` and `X-Shopify-Hmac-Sha256`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Utils::HmacValidator.validate` succeeds (it only checks `raw_body` against the secret) — see `lib/shopify_api/utils/hmac_validator.rb:13-22`.
5. `ShopifyAPI::Webhooks::Registry.process` builds `WebhookMetadata.new(shop: request.shop, ...)` with `request.shop == "victim-shop.myshopify.com"` (`lib/shopify_api/webhooks/registry.rb:198-199`) and invokes the app's handler as though the webhook genuinely originated from the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L16-33)
```ruby
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
