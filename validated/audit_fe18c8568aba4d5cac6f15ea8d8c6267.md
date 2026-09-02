### Title
Webhook Tenant Identity Spoofing via HMAC Not Covering Shop Domain - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable signature exclusively over the raw request body, while the `shop`, `topic`, `webhook_id`, and `api_version` fields used downstream for tenant identification and dispatch are read directly from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` trusts `request.shop` as the tenant identifier when constructing `WebhookMetadata` passed to the app's handler, even though that value is never part of the HMAC-signed bytes. This breaks the identity binding: `HMAC-verified bytes == raw_body` but `tenant identity acted upon == shop header`, which are not the same set of bytes.

### Finding Description
`Utils::HmacValidator.validate` computes the expected signature over `verifiable_query.to_signable_string` and compares it to the `hmac` value: [1](#0-0) 

For webhooks, `to_signable_string` returns only the raw request body: [2](#0-1) 

Meanwhile, `shop`, `topic`, `webhook_id`, and `api_version` are parsed straight from HTTP headers, which are not part of the HMAC's signed input: [3](#0-2) 

`Registry.process` validates the HMAC over the body only, then immediately trusts `request.shop` (a header value) as the tenant identity forwarded to the handler: [4](#0-3) 

This is the exact class of bug described by the rules: a field ("shop", acted upon as the tenant key for the handler) is not covered by the HMAC that is supposed to authenticate the request. The equality that should hold is:

`shop_bound_by_HMAC == shop_used_for_tenant_dispatch`

but in this gem it is actually:

`HMAC covers raw_body` vs `tenant dispatch uses shop header`

These are disjoint sets of bytes, so an attacker who possesses *any* valid `(raw_body, hmac)` pair (e.g., a legitimate webhook delivered to their own shop, where they have the app installed and can capture Shopify's real webhook delivery) can replay that exact body and HMAC to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header with a victim shop's domain. The HMAC check still passes because it only validates the body bytes, and the library reports `request.shop` as the victim's domain to the handler.

### Impact Explanation
If the consuming app relies on `WebhookMetadata#shop` (as documented/intended by this gem) to scope tenant data, look up the corresponding session, or attribute the webhook payload to a merchant, an attacker can force the app to process attacker-controlled, validly-signed webhook content under a victim tenant's identity — a cross-tenant confusion/spoofing primitive. This matches the Critical "cross-tenant access" impact category defined by the rules, since no per-tenant secret or access token is required to forge the identity binding; only a legitimate webhook payload from the attacker's own store is needed.

### Likelihood Explanation
Exploitation requires only that an attacker operate their own Shopify store with the target app installed (an unprivileged, ordinary merchant/developer capability) and forward captured webhook traffic to the target app's endpoint with a modified shop header — no `api_secret_key`, access token, or privileged access is required. The vulnerability is fully within this gem's own webhook verification logic (`Request#to_signable_string`, `Request#shop`, `HmacValidator.validate`, `Registry.process`) rather than depending on the host app misusing a documented API contract.

### Recommendation
Bind the shop identity to the HMAC-verified payload rather than trusting an unauthenticated header:
- Include the `shop-domain` (and ideally `topic`, `webhook-id`) header value in the signable string that is HMAC-verified, or
- Cross-check `request.shop` against a `shop_domain`/similar field embedded in the JSON body (which Shopify webhook payloads typically include), rejecting the request if they don't match, or
- Document explicitly that `Request#shop` is unauthenticated and must not be used for tenant-scoped authorization decisions without additional verification.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and registers a webhook subscription (e.g., `orders/create`).
2. Shopify delivers a legitimate webhook to the app's endpoint with body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(secret, B)` — valid per `HmacValidator.validate_signature`: [5](#0-4) 
3. Attacker captures `(B, H)` from their own delivered webhook (they have legitimate access to their own store's webhook traffic).
4. Attacker replays a request to the same app endpoint with the identical body `B` and header `X-Shopify-Hmac-Sha256: H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Request.new` accepts the request (all required headers present), and `Utils::HmacValidator.validate` returns `true` since it only checks `B` against `H`.
6. `Registry.process` calls the registered handler with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, causing the app to process attacker-supplied content as if it originated from the victim shop.

### Citations

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
