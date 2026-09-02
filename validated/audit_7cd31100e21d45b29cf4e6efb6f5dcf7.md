## Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `ShopifyAPI::Webhooks::Registry.process` validates that body against the HMAC using the app-wide `api_secret_key`. The `shop-domain` header, which `Registry.process` passes into the handler as the tenant identifier, is never part of the signed material. The identity binding broken is: `HMAC-verified bytes (raw body only)` ≠ `shop identity acted upon (shop-domain header)`.

### Finding Description
`Request#hmac` and `Request#to_signable_string` are defined as: [1](#0-0) 

Only `@raw_body` is fed into the signature check. The `shop` accessor pulls its value straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic tie to the body or to the HMAC: [2](#0-1) 

`Registry.process` verifies the HMAC and then hands `request.shop` directly to the app's handler as the authoritative tenant for the event: [3](#0-2) 

Crucially, `Utils::HmacValidator` signs/verifies using `Context.api_secret_key`, which is a single, app-wide secret shared across *every* shop that has installed the app — it is not a per-shop secret: [4](#0-3) 

Because the same secret authenticates webhooks for all tenants, and the `shop-domain` header is excluded from the signed payload, any party who can obtain one genuinely-signed webhook (raw body + valid HMAC) for their *own* shop can replay that exact body/HMAC pair while substituting an arbitrary `shopify-shop-domain` header value. `HmacValidator.validate` will still return `true` because it only checks the body bytes, and `Registry.process` will dispatch the handler believing the event originated from the victim shop specified in the header.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to provide: an unprivileged operator of any (even a free development) shop that has installed the target app can produce webhook requests that the app's handler will process as if they came from a different, victim shop. Any app logic keyed off `WebhookMetadata#shop` (e.g., updating per-shop settings, triggering redacts, revoking data, writing to per-shop records, session lookups) is exposed to cross-tenant injection of attacker-chosen bodies attributed to a shop the attacker does not control. This matches the "Critical - cross-tenant access" impact category, since it lets one tenant impersonate another at the identity-binding layer the gem is meant to enforce.

### Likelihood Explanation
Likelihood is bounded by two factors that keep this exploitable by an ordinary internet user without any special credentials from the target app or Shopify:
- Creating a Shopify partner/development store and installing the target public/custom app costs nothing and requires no privileged access to the victim's data.
- Once installed, Shopify will deliver genuinely signed webhooks (with the real `api_secret_key`) to the attacker's own shop for whichever body content Shopify computes (e.g., product/order create events reflecting attacker-supplied data such as titles), giving the attacker one or more valid `(body, HMAC)` pairs to replay with a forged `shop-domain` header against the same endpoint.
No possession of the victim's access token, the app's `client_secret`, or any credential belonging to the victim shop is required — only the ability to intercept/replay one's own legitimately-received webhook HTTP request with a modified header, which is fully within an unprivileged caller's control since headers are not covered by the signature.

### Recommendation
Bind the shop identity into the signed material, or otherwise cryptographically tie the `shop-domain` header to the verified request:
- Include the `shop-domain` (and ideally `topic`, `webhook-id`, `api-version`) header values in `to_signable_string` so the HMAC covers them, rejecting any request where the header used for dispatch was not part of what Shopify actually signed, or
- Independently corroborate `request.shop` against the shop encoded/expected for that webhook subscription (e.g., cross-check against the shop associated with the webhook registration id) before invoking the handler in `Registry.process`.
At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated header data and must never be trusted as a tenant boundary by consuming applications without additional verification.

### Proof of Concept
1. Attacker creates a free development shop and installs the target app (using the app's real `client_id`; no secret needed).
2. The app registers a webhook subscription (e.g., `products/create`) with the attacker's shop.
3. Attacker creates a product in their own shop; Shopify sends a webhook to the app's endpoint with headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC over raw body>`, and the JSON body.
4. Attacker captures this raw HTTP request (body + HMAC unchanged) and resends it to the same endpoint, changing only `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
5. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `@raw_body` only and succeeds because the body is unmodified — see `HmacValidator.validate_signature`: ` [5](#0-4) `
6. The registered handler is invoked with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)`, causing the app to process attacker-controlled data as an event belonging to the victim shop.

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
