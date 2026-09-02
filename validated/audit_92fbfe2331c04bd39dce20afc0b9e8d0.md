### Title
Webhook Shop-Domain Spoofing via HMAC That Only Covers the Raw Body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw HTTP body [1](#0-0) , while `shop` is read straight from the unauthenticated `X-Shopify-Shop-Domain`/`shopify-shop-domain` header [2](#0-1) . `Utils::HmacValidator.validate` verifies only that signable string (the body) against the app's shared `client_secret` [3](#0-2) , and `Registry.process` trusts that same unauthenticated `shop` value to build the tenant-identifying `WebhookMetadata` handed to the app's handler [4](#0-3) .

### Finding Description
The identity binding that should hold is:
`hmac(raw_body, client_secret) == received_hmac` **and** `shop ⊂ signed_bytes`.

In this gem, only the first half holds — `shop` is never part of `to_signable_string`, so the equality that actually gets enforced is `hmac(raw_body, client_secret) == received_hmac`, completely independent of `shop`.

Because the app's `client_secret` is shared across *every* shop that has this app installed, any merchant that legitimately installs the app can:
1. Trigger a webhook (e.g., `orders/create`) on their own store and capture the exact raw body plus its valid `X-Shopify-Hmac-Sha256` value delivered to the app's endpoint.
2. Replay that identical `(raw_body, hmac)` pair to the app's webhook endpoint, but swap the `X-Shopify-Shop-Domain` header to a victim shop's domain.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)` which only checks the body/hmac pair — it passes, since that part is unchanged [5](#0-4) .
4. The forged request is then dispatched to the handler as `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)` with `shop` equal to the attacker-chosen victim domain [6](#0-5) .

Any host application that keys per-tenant behavior off `WebhookMetadata#shop` (the documented and only tenant-identifying field the gem exposes for webhook processing) will process attacker-supplied data as though it originated from the victim's store — a break of the shop-authenticated vs. shop-acted-upon binding.

### Impact Explanation
This is a cross-tenant identity binding failure inside the gem's own webhook verification path (not a host-application misuse): the gem validates a signature that does not cover the very field (`shop`) it later reports as authenticated. Any consumer relying on `Registry.process`/`WebhookMetadata#shop` as gem-guaranteed tenant identity can be made to attribute attacker-controlled data to an arbitrary victim shop, meeting the "cross-tenant access" bar.

### Likelihood Explanation
Exploitation requires only that the attacker be an unprivileged installer of the target app on their own store (a normal, unprivileged capability) — no access to `client_secret`, no TLS interception, and no privileged account is needed. Capturing and replaying an HTTP request with a modified header is trivial.

### Recommendation
Include the shop domain (and other trust-relevant headers such as `topic`/`webhook-id`) inside the signable payload verified against the HMAC, or otherwise independently corroborate `shop` (e.g., cross-check against a per-shop stored token/registration) before trusting it in `WebhookMetadata`. At minimum, document prominently that `WebhookMetadata#shop` is not cryptographically bound by the HMAC check performed by this gem.

### Proof of Concept
1. Attacker installs the target app on `attacker.myshopify.com` and receives a legitimate webhook delivery with body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(client_secret, B)`.
2. Attacker resends the exact same request to the app's webhook endpoint, keeping `body: B` and `X-Shopify-Hmac-Sha256: H`, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)` parses successfully (all required headers present).
4. `ShopifyAPI::Webhooks::Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC-SHA256(client_secret, B)` and matches `H` — validation succeeds despite the shop being forged [5](#0-4) .
5. The registered handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and the attacker-originated body `B`, which the host app will treat as authentic data from the victim tenant [6](#0-5) .

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
