### Title
Webhook `shop-domain` Header Is Not Covered by HMAC, Allowing Cross-Tenant Shop Spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable payload from the raw HTTP body only, never including the `X-Shopify-Shop-Domain` header. `Webhooks::Registry.process` validates the HMAC and then unconditionally trusts `request.shop` (derived from that unauthenticated header) as the tenant identity passed to the app's webhook handler. This breaks the identity binding `HMAC-verified bytes == bytes the app trusts for tenant attribution`, letting anyone who can produce one validly-signed body (e.g. via their own shop's legitimate webhook deliveries, since `api_secret_key` is shared across all shops installing the app) attribute that body's data to an arbitrary victim shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is not part of the signable string: [2](#0-1) 

`Utils::HmacValidator.validate` only verifies `verifiable_query.to_signable_string` against `verifiable_query.hmac` — it has no notion of the `shop` field at all: [3](#0-2) 

`Registry.process` checks the HMAC, then immediately hands `request.shop` (the unauthenticated header) to the registered handler as authoritative tenant identity: [4](#0-3) 

The equality the code implicitly assumes but never enforces is:
`shop asserted in the request header == shop that the HMAC-signed body was actually generated for`

Because the `hmac-sha256` header only authenticates the request body bytes (and, by construction of `OpenSSL::HMAC.hexdigest`, proves the sender knew the shared `api_secret_key` — not which shop the payload is for), an attacker can take a validly-signed body (their own webhook delivery, since the same `api_secret_key` is used for every shop installing the app) and resend it with a different `shop-domain` header value. `HmacValidator.validate` still returns `true` because it never looks at the header, and `Registry.process` will happily invoke the handler claiming the payload belongs to the victim shop.

This exactly matches the report's described bug class: "a field acted on but not covered by the HMAC" — here, the `shop` field used for tenant attribution is acted upon by the handler but is completely outside the cryptographic envelope.

### Impact Explanation
This crosses a tenant boundary: the app relying on `WebhookMetadata#shop` (built from `request.shop`) to key per-shop state, invalidate caches, update local records, or make decisions bound to a specific merchant will process attacker-controlled data under a victim shop's identity. This satisfies the "Critical — cross-tenant access" bar: an unprivileged internet user (or any shop installing the same app) can inject data attributed to a shop they do not control, without needing the victim's access token or `api_secret_key`.

### Likelihood Explanation
Any actor who can install the app on their own shop (or otherwise obtain one legitimately HMAC-signed webhook body/HMAC pair, which is not shop-specific) can freely re-send that same body with a forged `X-Shopify-Shop-Domain` header directly to the app's public webhook endpoint. No secret material, TLS interception, or privileged account is required — only the ability to POST to the endpoint the host application exposes for `Webhooks::Registry.process`.

### Recommendation
Bind the `shop` (and ideally `topic`) to the HMAC-verified payload instead of trusting the header independently:
- Include `shop-domain` (and `topic`) in `Request#to_signable_string`, or
- Compare the header-derived shop against a shop value embedded in the signed body/topic-specific context, or
- At minimum, require the caller to supply the expected shop (e.g., from the URL route/session mapping already trusted by the host app) and assert it matches `request.shop` before invoking the handler, rejecting mismatches with `Errors::InvalidWebhookError`.

### Proof of Concept
1. Install the app on attacker-controlled shop `attacker.myshopify.com`; Shopify sends a legitimate webhook: body `B`, header `X-Shopify-Hmac-Sha256: H` (valid because it's HMAC(`B`, `api_secret_key`)), header `X-Shopify-Shop-Domain: attacker.myshopify.com`.
2. Attacker replays the exact same body `B` and HMAC `H` to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. Internally, the host app calls:
```ruby
ShopifyAPI::Webhooks::Registry.process(
  ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: { "x-shopify-hmac-sha256" => H, "x-shopify-shop-domain" => "victim.myshopify.com", "x-shopify-topic" => topic })
)
``` [4](#0-3) 
4. `Utils::HmacValidator.validate(request)` returns `true` (it only checks `B` against `H`), and the handler is invoked with `WebhookMetadata#shop == "victim.myshopify.com"`, even though the body actually originated from and pertains to `attacker.myshopify.com`. [5](#0-4)

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
