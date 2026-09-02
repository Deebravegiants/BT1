This confirms the finding. `WebhookMetadata#shop` at [1](#0-0)  is populated directly from `request.shop`, which is read from the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` header, while `HmacValidator` only authenticates `@raw_body` via `to_signable_string`.

### Title
Webhook shop identity is taken from an unauthenticated header not covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` attribute exclusively from the `shopify-shop-domain` HTTP header, while `Utils::HmacValidator.validate` (used in `Registry.process`) only verifies the raw request body against the HMAC signature. The header carrying the shop identity is never part of the signed material, so an attacker who possesses one valid `(body, hmac)` pair can replay it with an arbitrary `shop-domain` header and have it accepted as authentic for a different shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [2](#0-1)  and `Request#shop` is read straight from headers with no cryptographic binding to the signed body: [3](#0-2) .

`Registry.process` validates the HMAC and, once it passes, immediately trusts `request.shop` to build the `WebhookMetadata` passed to the app's handler: [4](#0-3) . `HmacValidator.validate`/`validate_signature` only ever authenticate `verifiable_query.to_signable_string` (the body), never the shop header: [5](#0-4) .

This is precisely the "field acted on but not covered by the HMAC" identity-binding break: the equality the code implicitly assumes is `authenticated_shop == request.shop`, but what is actually authenticated is only `HMAC(body) == received_hmac`, with `shop` left completely outside that proof. Any request whose body+HMAC pair is valid for *some* shop will be accepted and attributed to *whatever* `shop-domain` header the requester chooses to send, because the header is attacker-controlled and unauthenticated.

### Impact Explanation
This breaks cross-tenant isolation (Critical impact category "cross-tenant access"). A host application that uses `WebhookMetadata#shop` — the field this gem provides specifically for that purpose — to look up a merchant's session/tenant record and act on webhook data (e.g., delete tenant data for `shop/redact`, `customers/redact`, `customers/data_request`, or update tenant billing/subscription state) will perform that tenant-scoped action against the attacker-chosen `shop` value instead of the shop whose data was actually authenticated by the HMAC. This lets an attacker who obtains a single legitimate `(body, hmac)` pair (e.g., from their own store's genuine webhook deliveries, which they are entitled to receive as an app-installing merchant) redirect its effect onto any other shop domain merely by changing the header.

### Likelihood Explanation
Moderate-to-high: no secret material is required to exploit this — only one legitimately-received webhook body/HMAC pair (which any installing merchant naturally obtains from their own store's normal webhook traffic) plus the ability to POST directly to the app's public webhook endpoint with modified headers. The library does nothing to prevent or warn against this; `Request` and `HmacValidator` treat the header-derived `shop` as trustworthy once the body HMAC checks out.

### Recommendation
Bind the shop identity to the signed material, e.g., include the `shop-domain` (and ideally `topic`/`webhook-id`) header value inside the string that is HMAC-verified (`to_signable_string`), or otherwise cryptographically tie the header to the body before exposing `WebhookMetadata#shop` to handlers. At minimum, document in `IInterestRateModel`-style specs (i.e., the `VerifiableQuery`/`Request` docs) that `shop` is unauthenticated and must not be trusted for tenant-scoping decisions without independent verification (e.g., cross-checking against a shop already on file for that webhook's HMAC secret, if per-shop secrets are used).

### Proof of Concept
1. Attacker legitimately installs the app on `attacker-shop.myshopify.com` and receives a genuine webhook delivery, capturing the raw body `B` and its header `x-shopify-hmac-sha256: H` (valid because `H = HMAC_SHA256(api_secret_key, B)`).
2. Attacker sends a POST to the app's public webhook endpoint with the same raw body `B` and header `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Request.new` parses headers, and `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC_SHA256(api_secret_key, B)` and compares it to `H` — this succeeds because the body was not modified: [6](#0-5) .
4. `Registry.process` proceeds to call `handler.handle(data: WebhookMetadata.new(..., shop: request.shop, ...))` with `shop == "victim-shop.myshopify.com"`, even though the payload/HMAC never authenticated anything about `victim-shop`: [7](#0-6) .
5. The host application's handler, trusting `data.shop` as the authenticated tenant identifier, performs a tenant-scoped action (e.g. data deletion/redaction, or state change) against `victim-shop`, achieving cross-tenant impact without ever needing `victim-shop`'s credentials.

### Citations

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
