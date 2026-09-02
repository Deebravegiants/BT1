### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/registry.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, then trusts the unauthenticated `x-shopify-shop-domain` (or `shopify-shop-domain`) header as the tenant identity handed to the app's webhook handler. Because the shop-domain header is never included in the signed material, any actor who can produce one valid `(raw_body, hmac)` pair signed with the app's shared `client_secret` can relabel it with an arbitrary shop domain and have the app process it as belonging to a different merchant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read straight from an HTTP header with no cryptographic binding to the body or to the HMAC: [2](#0-1) 

`Registry.process` validates only the HMAC of the request (i.e., of the raw body) and then immediately trusts `request.shop` as the tenant key that gets forwarded to the app's handler: [3](#0-2) 

`HmacValidator.validate` simply recomputes the HMAC of `to_signable_string` (the body) using `Context.api_secret_key` and compares it to the supplied `hmac`; it never touches headers: [4](#0-3) 

Shopify signs webhooks with the app's single `client_secret`, which is identical for every shop that has the app installed — it is not per-shop. Consequently, the identity binding the code needs is:

```
shop_used_as_tenant_key (header, unauthenticated) == shop_that_actually_produced(raw_body, hmac)
```

but the code only checks:

```
hmac == HMAC(api_secret_key, raw_body)
```

with the `shop` value fully disjoint from what is signed. This is the same class of bug described in the report: a field that drives downstream identity/tenant decisions (there, the referral code binding; here, the webhook's shop) is mutable/attacker-controlled independent of the authenticated data it's supposed to travel with.

### Impact Explanation
Any party that legitimately receives (or can trigger) a webhook for *any* shop that has the vulnerable app installed — including their own store, which they fully control — obtains a `(raw_body, hmac)` pair valid under the app's shared secret. They can replay that exact body/HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header for a victim shop's domain. `HmacValidator.validate` still passes (it never looked at the header), so `Registry.process` invokes the app's handler with `WebhookMetadata#shop` set to the victim's domain and attacker-controlled body content. Any host application that uses `data.shop` to key session/data lookups (a documented, expected use, see `WebhookMetadata`) will now write attacker data into, or read/act on behalf of, another tenant's account — a cross-tenant access condition.

### Likelihood Explanation
The prerequisite is only that the attacker installs the target app on their own (or any) shop — a normal, low-privilege action available to any merchant/internet user for public apps — and can send crafted HTTP requests to the app's public webhook endpoint, which by design must be internet-reachable. No secrets, tokens, or admin access are required.

### Recommendation
- Include the shop domain (and ideally the topic/webhook id) inside the HMAC-signed material, or otherwise cryptographically bind the header values used for tenant identification to the signed payload.
- Alternatively, require callers to independently corroborate `request.shop` against another authenticated source (e.g., correlate to a known session/API version created during OAuth) rather than trusting the header outright.
- At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated and must not be used as a tenant key without additional verification, and provide a validated equivalent for library consumers.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`.
2. Attacker triggers any webhook topic the app registers (e.g., `orders/create`) on their own shop, capturing the raw POST body and the `x-shopify-hmac-sha256` header sent by Shopify (signed with the app's shared `client_secret`).
3. Attacker resends the exact same body and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Utils::HmacValidator.validate` (via `Registry.process`) recomputes the HMAC over the raw body only and it matches, so the request is accepted.
5. `WebhookMetadata.new(..., shop: request.shop, ...)` is built with `shop = "victim-shop.myshopify.com"`, and the app's handler processes attacker-supplied data under the victim shop's identity — demonstrating the cross-tenant binding break at: [5](#0-4)

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
