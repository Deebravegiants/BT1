### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook's authenticity using only the raw request body against `x-shopify-hmac-sha256`, but the `shop` (and `topic`/`api_version`/`webhook_id`) values that are handed to the app's handler are read directly from unauthenticated HTTP headers. The identity binding "HMAC-verified bytes == bytes the handler trusts for tenant identification" is broken: the HMAC only binds the body, not the `shop-domain` header.

### Finding Description
`Utils::HmacValidator.validate` computes the HMAC purely over `verifiable_query.to_signable_string`, and for webhooks `to_signable_string` returns only `@raw_body`: [1](#0-0) [2](#0-1) 

Meanwhile `Registry.process` fetches `request.shop` — a value taken straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header — and forwards it, unverified, into the `WebhookMetadata` struct passed to the app's `WebhookHandler#handle`: [3](#0-2) [4](#0-3) [5](#0-4) 

Because the HMAC only covers `@raw_body`, an unprivileged internet user who has captured (or can otherwise obtain, e.g. by triggering their own store's webhook) one genuine `(body, hmac)` pair from Shopify can replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header value. `HmacValidator.validate` will still succeed (it never inspects the header), and `Registry.process` will call the handler with `WebhookMetadata#shop` set to the attacker-chosen shop domain instead of the shop the body actually originated from.

### Impact Explanation
Any app that uses `WebhookMetadata#shop` to key data storage, tenant lookups, or trigger side effects (e.g., "update this shop's order record", "look up shop X's settings") is exposed to cross-tenant data corruption/access: an attacker-controlled `shop` value reaches trusted business logic despite the HMAC check passing, letting an attacker mislabel a webhook payload as belonging to a different, victim tenant. This matches the report's bug class — a field acted upon (`shop`) that is not covered by the authenticity check (HMAC over body only) — applied here as a genuine cross-tenant identity-binding break, qualifying as Critical/cross-tenant impact per the given rules.

### Likelihood Explanation
Exploitation requires the attacker to possess at least one valid `(raw_body, hmac)` pair signed with the app's secret for some topic — obtainable without needing the `api_secret_key` itself, e.g. by installing the app on their own shop and capturing a legitimate webhook delivery to their own endpoint, then replaying it against the same app's webhook endpoint with a forged `shop-domain` header. No credential leakage or privileged access is required, only observation of one's own legitimate webhook traffic, so likelihood is moderate-to-high for any app that provisions per-tenant behavior from `WebhookMetadata#shop`.

### Recommendation
Include the `shop`, `topic`, and `webhook_id` header values in the signable string (or otherwise cryptographically bind them into the HMAC input) so that tampering with any header invalidates the signature, not just tampering with the body. Alternatively, `Registry.process`/`Request` should independently verify that the `shop` supplied in the header matches a shop domain the app has an active session/installation for before dispatching to the handler.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and receives a legitimate webhook: body `{"id":1}` with header `x-shopify-hmac-sha256: <valid HMAC of body>` and `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker replays the exact same body and HMAC header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `Utils::HmacValidator.validate` recomputes the HMAC over `@raw_body` only — unchanged — and returns `true`. [6](#0-5) 
4. `Registry.process` builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` using `shop == "victim.myshopify.com"` even though the body was never issued for that shop, and dispatches it to the app's handler as an authentic event for the victim tenant. [7](#0-6)

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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
