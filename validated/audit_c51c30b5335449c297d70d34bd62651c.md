## Analysis

I found a valid analog. In `lib/shopify_api/webhooks/request.rb`, the `Request` class computes its HMAC-signable content as *only* the raw body: [1](#0-0) 

But the tenant-identifying and routing fields — `shop`, `topic`, `api_version`, `webhook_id` — are all read directly from unauthenticated HTTP headers, completely outside the HMAC coverage: [2](#0-1) [3](#0-2) 

`Registry.process` validates only that HMAC (which covers the body bytes, not the headers), then trusts `request.shop` and `request.topic` from those unauthenticated headers to dispatch to a handler and construct `WebhookMetadata`: [4](#0-3) 

This is the exact bug-class analog called out in the rules: **a field acted on (`shop`, `topic`) is not covered by the HMAC**. `HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:12-31`) only proves the `raw_body` bytes are unmodified relative to the secret; it proves nothing about which shop or topic that body is claimed to belong to. [5](#0-4) 

### Title
Webhook HMAC does not bind the `shop`/`topic` headers, allowing cross-tenant webhook replay - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so the HMAC signature verified by `HmacValidator.validate` authenticates the request body bytes but not the `X-Shopify-Shop-Domain`, `X-Shopify-Topic`, `X-Shopify-Webhook-Id`, or `X-Shopify-Api-Version` headers, which are read unauthenticated and passed straight into `Registry.process` and `WebhookMetadata`.

### Finding Description
`Registry.process` performs exactly one authenticity check — `Utils::HmacValidator.validate(request)` — before dispatching the webhook to the registered handler with `request.shop` and `request.topic`. Because `Request#to_signable_string` (`lib/shopify_api/webhooks/request.rb:35-38`) only returns the raw body, an attacker who possesses *any* validly-signed body+HMAC pair (e.g., from a webhook legitimately delivered to their own shop, since a merchant/attacker who installs the app receives real webhooks with valid signatures for their own tenant) can resend that exact body and HMAC to the app's webhook endpoint while substituting arbitrary values for the `shop-domain` and `topic` headers. The HMAC check passes unchanged because it never inspected those headers, and the app's handler is invoked believing the payload originates from, and pertains to, a different, victim shop and/or a different (potentially more sensitive, e.g. mandatory GDPR) topic.

This breaks the identity binding: `shop authenticated (by HMAC) == shop used for tenant-scoped processing`. Here the left side is always true for the same secret regardless of header content, while the right side (`request.shop`) is attacker-controlled.

### Impact Explanation
This enables cross-tenant confusion: a party holding one valid signed webhook can relabel it to impersonate a different shop or topic, causing the host application to process or store data under, or trigger topic-specific side effects (including mandatory `customers/redact`/`shop/redact` handling if the host app wires those through the same handler dispatch) for, a shop the attacker does not own. This matches the "Critical - cross-tenant access" category since tenant-scoped webhook data/processing can be attributed to the wrong merchant.

### Likelihood Explanation
Requires the attacker to already have received one legitimately signed webhook (trivial for anyone who installs the app on their own store, since apps commonly send webhooks to a shared, often-public endpoint) and to resend it with modified headers to the same endpoint — no access to `client_secret` or another merchant's credentials is needed.

### Recommendation
Include the tenant/topic-identifying headers (`shop`, `topic`, `webhook_id`, `api_version`) in the signable content used for HMAC verification, or otherwise cryptographically bind them to the signed body, so that the HMAC authenticates the header claims that `Registry.process` and `WebhookMetadata` rely on — not just the raw body bytes.

### Proof of Concept
1. Attacker installs the app on their own shop `attacker.myshopify.com` and receives a legitimate webhook, e.g. `orders/create`, with body `B` and header-derived HMAC `H` (valid because `H = HMAC(secret, B)`).
2. Attacker replays a POST to the app's webhook endpoint with the same body `B` and `X-Shopify-Hmac-Sha256: H`, but sets `X-Shopify-Shop-Domain: victim.myshopify.com` and `X-Shopify-Topic: customers/redact`.
3. `HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:12-22`) recomputes the HMAC over `B` only, finds it matches `H`, and returns `true`.
4. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) dispatches to the `customers/redact` handler with `shop: "victim.myshopify.com"`, even though the body content and its signature never attested to that shop or topic.

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
