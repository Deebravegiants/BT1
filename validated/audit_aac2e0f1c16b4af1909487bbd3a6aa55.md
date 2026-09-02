### Title
Webhook `shop` field not covered by HMAC signature allows cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the merchant identity (`shop`) from the `X-Shopify-Shop-Domain` HTTP header, but the HMAC signature that `Utils::HmacValidator` verifies is computed only over the raw request body (`to_signable_string` returns `@raw_body`). Because the app's `client_secret`/`api_secret_key` used to compute the HMAC is the same for every shop that has installed the app, a party that legitimately receives one webhook (e.g., the operator of their own installed test shop) can replay that same body+HMAC pair to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header. The signature still validates, but the shop identity attached to the processed webhook is attacker-controlled.

### Finding Description
`Request#hmac` reads the `hmac-sha256` header and `Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is pulled straight from the `shop-domain` header, which is not part of the signed content: [2](#0-1) 

`Registry.process` validates the HMAC over the body only, then trusts `request.shop` (the unauthenticated header) to build `WebhookMetadata` and dispatches it to the app's handler: [3](#0-2) 

`Utils::HmacValidator.validate` only recomputes the signature over `verifiable_query.to_signable_string` (i.e. the raw body) and secure-compares it to the `hmac` header — it never binds the `shop` header into the signature: [4](#0-3) 

The identity binding that should hold is:
`shop the HMAC secret authenticates == shop attributed to the processed webhook (request.shop)`

Because the same `api_secret_key` is shared across every shop that installs the app (it's a per-app secret, not per-shop), and because `shop-domain` is excluded from the signed bytes, an attacker who controls (or has intercepted) any one genuine webhook delivery for *their own* shop can resend the identical `raw_body` + `hmac-sha256` header to the app's webhook endpoint with a forged `shopify-shop-domain` header naming a victim shop. `HmacValidator.validate` still returns `true` (the body and HMAC are genuinely matched), so `Registry.process` proceeds and invokes the registered handler with `shop: request.shop` set to the victim's shop domain — even though the payload content actually originated from, and was signed for, the attacker's own shop.

### Impact Explanation
This breaks the tenant/shop authentication boundary that webhook processing is supposed to enforce: the gem asserts "this payload is authentically from Shopify for shop X" but the shop identifier consumed by application handlers is never included in what is cryptographically verified. Any handler logic keyed on `WebhookMetadata#shop` (e.g., mandatory compliance topics like `customers/redact`, `shop/redact`, or app-specific per-shop state updates/uninstall handling) can be triggered against a shop the attacker does not control, using data the attacker fully manufactures via their own legitimately-signed webhook traffic. This is a cross-tenant action within the classification of Critical severity (cross-tenant access) as defined by the ruleset.

### Likelihood Explanation
Medium-High: exploitation requires the attacker to possess a valid `(raw_body, hmac-sha256)` pair from a webhook Shopify sent them, which they trivially have if they install the target app on their own store (a normal, unprivileged action) and then capture any webhook delivery. No access to the app's `client_secret`, tokens, or victim credentials is required — only the ability to POST directly to the app's public webhook endpoint with modified headers, which is standard unauthenticated HTTP access.

### Recommendation
Bind the shop identity into the verified signature material, or otherwise authenticate `shop-domain` against a source of truth before use:
- Prefer requiring callers to independently verify `X-Shopify-Shop-Domain` against a previously known/installed shop record before trusting it for `WebhookMetadata`, rather than relying solely on the payload-only HMAC.
- Alternatively, since Shopify's own webhook HMAC intentionally only covers the body, the gem (or its documentation) should make explicit that `request.shop` is unauthenticated header data and must be cross-checked by the consuming app against its own session/shop store before being used to gate or scope any tenant-specific action — currently `Registry.process` passes it straight through without such a caveat enforced in code.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` (a legitimate, unprivileged action).
2. Shopify sends a genuine webhook to the app's endpoint: body `B`, headers include `X-Shopify-Hmac-Sha256: H` (valid for `B` under the app's shared `api_secret_key`) and `X-Shopify-Shop-Domain: attacker.myshopify.com`.
3. Attacker captures `B` and `H`, then sends a new POST to the same webhook endpoint with identical body `B` and header `X-Shopify-Hmac-Sha256: H`, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {..., "shop-domain" => "victim.myshopify.com", "hmac-sha256" => H, ...})` is constructed; `Utils::HmacValidator.validate(request)` recomputes HMAC over `B` only and it matches `H`, so validation succeeds (`lib/shopify_api/utils/hmac_validator.rb:12-31`).
5. `Registry.process(request)` proceeds and calls `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: "victim.myshopify.com", ...))` (`lib/shopify_api/webhooks/registry.rb:189-200`), causing the app to process attacker-controlled data as belonging to `victim.myshopify.com`.

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

**File:** lib/shopify_api/webhooks/registry.rb (L189-200)
```ruby
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
