### Title
Webhook `shop` (and `topic`/`webhook-id`) identity is trusted from unauthenticated headers while the HMAC only covers the request body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, and `HmacValidator.validate` verifies that HMAC against `Context.api_secret_key`. The `shop`, `topic`, `api_version`, and `webhook_id` values, however, are read straight from HTTP headers and are never included in the signed material. `Registry.process` only checks the body's HMAC and then hands the handler a `WebhookMetadata` built from those unauthenticated headers, including `shop: request.shop`.

### Finding Description
The identity binding that should hold is:
`shop that cryptographically produced/authorized this webhook == shop attributed to the delivered data`

What is actually checked:
- `HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:26-31`) verifies `OpenSSL.secure_compare(computed_signature, received_signature)` where `computed_signature` is `HMAC-SHA256(api_secret_key, to_signable_string)`.
- `Webhooks::Request#to_signable_string` (`lib/shopify_api/webhooks/request.rb:35-38`) returns `@raw_body` only — headers are excluded from the signed material.
- `Webhooks::Request#shop` (`lib/shopify_api/webhooks/request.rb:20-23`) reads `shopify-shop-domain`/`x-shopify-shop-domain` directly, with no relation to the HMAC.
- `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) raises only if `Utils::HmacValidator.validate(request)` is false, then immediately builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)` and dispatches it to the app's handler.

Because `api_secret_key` is the app's single client secret shared across **every** shop that has installed the app, a valid HMAC only proves "Shopify (or holder of the app secret) produced this body" — it proves nothing about which shop the body belongs to. Any tenant that has legitimately installed the app receives genuine webhook deliveries with a valid HMAC over the body. That attacker-controlled tenant can capture one such (body, HMAC) pair from their own shop and replay it to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header (e.g., a victim shop). `HmacValidator.validate` still succeeds because it only checks the body bytes, and `Registry.process` will pass the forged `shop` straight to the handler as authoritative tenant identity.

### Impact Explanation
If the host application (as the gem's documented API pattern of `WebhookMetadata#shop` and `Registry.process` implies) uses `data.shop` to select which merchant record, session, or access token to act on, this allows cross-tenant data injection/confusion: an attacker with their own valid installation can make the app process replayed webhook payloads under a victim shop's identity. This crosses a tenant boundary using only a legitimately-obtained (from the attacker's own installation) HMAC, matching the "Critical - cross-tenant access" impact class, since the field driving tenant attribution (`shop`) is not bound by the same cryptographic check that authenticates the payload.

### Likelihood Explanation
Requires only that the attacker be a legitimate but unprivileged installer of the target app on their own shop (no special privileges, no access to the app's `client_secret`, no leaked credentials) — the same trust level the "unprivileged internet user" persona describes. Capturing one's own webhook deliveries and replaying them with a different `shop-domain` header is trivial via any HTTP client.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the HMAC-covered material where possible, or — since Shopify's actual delivery signature only ever covers the body — require the host application to independently validate that `request.shop` corresponds to an actual installed/known session for the app before trusting it, and document this prominently. At minimum, `Registry.process` / `WebhookMetadata` should not implicitly present `request.shop` as an authenticated value; the gem should make explicit that only body integrity, not sender/tenant identity, is established by `HmacValidator.validate`.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and receives a legitimate webhook delivery:
   - Headers: `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC of body>`, `x-shopify-topic: orders/create`
   - Body: `{"id": 1, ...}`
2. Attacker resends the exact same body and HMAC header to the app's webhook endpoint, only changing:
   - `x-shopify-shop-domain: victim.myshopify.com`
3. `ShopifyAPI::Webhooks::Request.new` parses headers/body as usual (`lib/shopify_api/webhooks/request.rb:46-63`).
4. `Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `raw_body` only and matches — validation passes (`lib/shopify_api/webhooks/registry.rb:190`, `lib/shopify_api/utils/hmac_validator.rb:13-22`).
5. The handler receives `WebhookMetadata.new(topic: "orders/create", shop: "victim.myshopify.com", body: {...}, ...)` — data belonging to the attacker's shop is now falsely attributed to the victim shop, with no cryptographic re-check of the `shop` claim. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

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
