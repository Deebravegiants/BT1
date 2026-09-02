### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` extracts the `shop` identity for a webhook exclusively from the `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header, but this header is never included in the bytes that are HMAC-verified. `Registry.process` only checks the HMAC of the raw body, then trusts the header-derived `shop` value when building `WebhookMetadata` that is handed to the app's handler.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read from a header that is completely separate from the signed content: [2](#0-1) [3](#0-2) 

`Registry.process` validates only the HMAC of the body, then immediately trusts `request.shop` for dispatch/metadata without any binding between the two: [4](#0-3) 

The resulting `WebhookMetadata` struct — passed to the app's `WebhookHandler#handle` — carries the unauthenticated `shop` value as if it were verified: [5](#0-4) 

The identity-binding equality this breaks: `bytes verified (raw_body via HMAC) != bytes trusted for tenant identity (shop-domain header)`. Shopify webhooks for a given app are all signed with the same app-level `client_secret`, not a per-shop secret, so the HMAC only proves "this body was signed by the app's own secret" — it does **not** prove which shop the payload belongs to. Any user who has legitimately installed the target app on their own store (an "unprivileged internet user" from the app's perspective — anyone can install a public app) will receive real webhook deliveries with valid `raw_body` + `hmac` pairs for their own shop. Because the `shop-domain` header is not part of the signed content, that same attacker can replay the exact `raw_body`/`hmac` pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header value (e.g., a victim shop that also has the app installed). The HMAC check in `Utils::HmacValidator.validate` still passes (it only re-computes HMAC over `raw_body`), so `Registry.process` will dispatch attacker-controlled body content to the app's handler labeled as belonging to the victim's tenant.

### Impact Explanation
This breaks the tenant boundary the webhook system is meant to enforce: an attacker who owns/controls one shop can inject data into the handler logic that a merchant-facing app associates with a *different* shop's tenant (e.g., forging an `orders/create`, `app/uninstalled`, or `shop/redact` event attributed to a victim shop). Depending on what the host application does inside its `WebhookHandler#handle` implementation (e.g., updating per-shop billing state, revoking access, writing to a shop-scoped database record keyed by `data.shop`), this can result in cross-tenant data corruption or logic execution against a shop the attacker does not control — satisfying the "cross-tenant access" criterion for High/Critical impact.

### Likelihood Explanation
Medium-High. The prerequisite is only that the attacker be able to install the target app on a shop they control (trivial for any public Shopify app) and capture one legitimate webhook delivery (raw body + HMAC header), which any installed merchant automatically receives. No access token, `client_secret`, or privileged account is required — only a normal, unprivileged app installation.

### Recommendation
Bind the claimed `shop` (and other identifying headers such as `topic`, `webhook-id`, `api-version`) into the HMAC-verified content, or otherwise cryptographically tie the header values to the signed body (e.g., include them in the signable string, similar to how `AuthQuery#to_signable_string` includes `shop`). At minimum, cross-check the `shop-domain` header against an independently-verified per-shop session/secret before trusting it in `WebhookMetadata`.

### Proof of Concept
1. Install the target Shopify app on attacker-controlled store `attacker.myshopify.com`; trigger a webhook (e.g., `orders/create`) so Shopify sends a legitimate POST with body `raw_body` and header `x-shopify-hmac-sha256: <valid HMAC of raw_body under the app's shared client_secret>`.
2. Capture that request.
3. Replay the identical `raw_body` and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but change `x-shopify-shop-domain` to `victim.myshopify.com` (a different shop that also has the app installed).
4. `Utils::HmacValidator.validate` in `Registry.process` succeeds because it only checks `raw_body` against the shared secret's HMAC: [6](#0-5) 
5. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and `body` fully controlled by the attacker, despite the payload actually originating from and describing the attacker's own shop.

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

**File:** lib/shopify_api/webhooks/request.rb (L65-70)
```ruby
      private

      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
