Confirmed the finding. The `Webhooks::Request` HMAC covers only the raw body via `to_signable_string` returning `@raw_body`, while `shop` (and `topic`, `api_version`, `webhook_id`) are pulled from unauthenticated headers and never enter the signable string.

### Title
Cross-Tenant Webhook Attribution via Unsigned Shop-Domain Header - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw body only, but the `shop` (and `topic`/`webhook_id`) values used by `Registry.process` to attribute and route the webhook are read from HTTP headers that are excluded from the signed payload.

### Finding Description
`Request#to_signable_string` returns `@raw_body` exclusively [1](#0-0) , and `Request#shop` is derived purely from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic binding to the body or HMAC [2](#0-1) . `Registry.process` validates only `Utils::HmacValidator.validate(request)`, which in turn calls `validate_signature` comparing the HMAC of `to_signable_string` (the body) against the received signature [3](#0-2) . After this single check passes, `Registry.process` builds `WebhookMetadata` using `request.shop` taken straight from the unauthenticated header, and dispatches it to the app's handler [4](#0-3) .

Since the app's `client_secret`/`api_secret_key` is a single shared secret used to sign webhooks for *all* shops on the app (not a per-shop secret), a valid `(body, hmac)` pair obtained from any one shop's legitimate webhook delivery remains cryptographically valid for that same body regardless of which `shop-domain` header accompanies it. The intended identity binding is: `shop header used by handler == shop that produced the signed body`. Because `shop` is not covered by `to_signable_string`, this equality is never enforced — an attacker can swap the `shop-domain` header on a replayed request without invalidating the HMAC.

### Impact Explanation
An attacker who operates their own Shopify store (an unprivileged merchant/internet user with respect to the *target* app) can install the target app on their own store, receive a legitimately signed webhook (valid body + HMAC using the app's shared secret), then replay that exact body/HMAC to the app's webhook endpoint while substituting a different `X-Shopify-Shop-Domain` header naming a victim shop. `Registry.process` will accept the HMAC (it only checks the body) and hand the handler `WebhookMetadata` claiming the data belongs to the victim shop [5](#0-4) . Any app logic that trusts `data.shop`/`WebhookMetadata#shop` for tenant-scoped writes, lookups, or access decisions (e.g., updating a customer/order record keyed by shop, honoring `shop/redact` or `customers/redact` for the wrong tenant) is exposed to cross-tenant data corruption or disclosure — this satisfies the Critical "cross-tenant access" impact criterion.

### Likelihood Explanation
Moderate-to-high: the attacker needs only their own store with the target app installed to obtain a valid `(body, hmac)` pair, then a trivial HTTP replay with a modified header. No access to the target's or any victim's credentials, TLS interception, or social engineering is required — only the ability to receive one webhook the app itself sends to the attacker's own shop.

### Recommendation
Include `shop` (and ideally `topic`/`webhook_id`) in the signed payload verified by `Utils::HmacValidator`, or otherwise cryptographically bind the header-derived `shop` to the signed body (e.g., require the app to additionally verify the well-known shop domain against the resolved GraphQL/session context before trusting `WebhookMetadata#shop`) rather than trusting it purely from an unauthenticated header.

### Proof of Concept
1. Install the target app on attacker-owned shop `attacker.myshopify.com`; trigger any subscribed webhook topic (e.g., `orders/create`) to receive `raw_body` and a valid `X-Shopify-Hmac-SHA256` header.
2. Replay the identical raw body and HMAC header to the app's webhook endpoint, but set `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (the unchanged body) and succeeds [6](#0-5) .
4. `request.shop` returns `"victim.myshopify.com"` from the forged header [2](#0-1) , and the app's handler receives `WebhookMetadata` attributing attacker-controlled data to the victim shop.

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
