### Title
Webhook `shop-domain` header is not covered by HMAC verification, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `ShopifyAPI::Webhooks::Registry.process` uses the `shop-domain` header value (`request.shop`) as the authoritative tenant identifier for a webhook without that value ever being included in the HMAC-verified data. This breaks the identity binding `HMAC-verified bytes == data acted on`, since the header that determines *which shop* the webhook applies to is disjoint from the HMAC-covered payload.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements the `Utils::VerifiableQuery` interface. Its `to_signable_string` method only returns `@raw_body`: [1](#0-0) 

Its `shop` accessor, however, reads directly from the unauthenticated `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header: [2](#0-1) 

`Utils::HmacValidator.validate` only calls `compute_signature(verifiable_query.to_signable_string, secret)` and compares it to the received HMAC — it never incorporates the shop-domain header into the signed material: [3](#0-2) 

`Registry.process` validates only this body-only HMAC, and then dispatches the handler using `request.shop` as the tenant identity for the webhook payload: [4](#0-3) 

The binding the code implicitly assumes is:
`HMAC_valid(raw_body) == (raw_body, shop) is authentic for shop`

But the actual guarantee provided is only:
`HMAC_valid(raw_body) == raw_body was produced with knowledge of api_secret_key`

The `shop` value is never part of the signed bytes, so any two requests with the same raw body but different `shop-domain` headers pass identical HMAC verification. An attacker who legitimately receives one authentic webhook delivery (raw body + valid HMAC) for a shop it controls can replay that exact `(raw_body, hmac)` pair to the app's public webhook endpoint while substituting an arbitrary victim `shop-domain` header. The library will accept it as valid and hand `WebhookMetadata` with the attacker-chosen `shop` to the app's handler.

### Impact Explanation
This is a cross-tenant identity confusion at the library boundary: the value host applications are expected to trust as "which merchant this webhook is for" is not authenticated, only the body is. For topics where the body content doesn't already bind to a specific shop (e.g., `app/uninstalled`, `shop/redact`, `customers/redact`, `customers/data_request`, or any custom/generic payload), an attacker with one valid app-installed shop can force the handler to process privileged/mandatory compliance webhooks (like `shop/redact` or `customers/data_request`) against an arbitrary victim shop domain, since `Registry.process` dispatches to handlers using the untrusted `request.shop` value. This can lead to cross-tenant data actions (e.g., app treating a victim shop as uninstalled/redacted, or acting on the attacker's data under a spoofed shop identity), which is a High/Critical severity boundary violation of merchant-tenant isolation, consistent with the "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires the attacker to control at least one legitimate shop that has the app installed (to obtain a genuine `raw_body` + `hmac` pair) and the ability to send an HTTP request to the app's public webhook endpoint with a modified `shop-domain` header — both are within reach of an unprivileged but genuine app-installing user, with no access token, secret, or privileged account required. Likelihood is moderate: it depends on the host application actually keying tenant-scoped logic off `WebhookMetadata#shop` (which is the documented/intended use of this field), and it is more impactful for topics whose payload is shop-agnostic.

### Recommendation
Bind the shop-domain header into the value verified by HMAC, or otherwise cryptographically tie `request.shop` to the signed payload before it is trusted downstream. Concretely, `Utils::HmacValidator`/`Webhooks::Request` should either (a) document and enforce that `shop-domain` must never be used for authorization-sensitive branching without an out-of-band trust boundary (e.g., verifying via mTLS/IP allow-list at the transport layer, which is outside this gem), or (b) require callers to independently confirm that `request.shop` corresponds to a shop with a valid, existing offline session/access token in their session storage before acting on the webhook, rejecting webhooks for unknown/mismatched shops. At minimum, the library should surface a clear warning in `WebhookMetadata`/`Registry.process` that `shop` is unauthenticated header data, distinct from the HMAC-verified body.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and lets Shopify deliver a genuine webhook (e.g. `app/uninstalled`) to the app's endpoint, capturing the raw request body `B` and its valid header `x-shopify-hmac-sha256: H` (computed by Shopify over `B` using the shared `api_secret_key`).
2. Attacker resends the same body `B` and same header `H` to the app's webhook endpoint, but replaces `x-shopify-shop-domain` with `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` accepts the request (all required headers present), and `Utils::HmacValidator.validate` succeeds because it only checks `HMAC(B, secret) == H`, per: [5](#0-4) 
4. `Registry.process` calls the registered handler with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: ..., ...)`, per: [6](#0-5) 
5. The host application's handler (following the gem's documented usage pattern) now performs shop-scoped actions (e.g., deactivating/redacting data) against `victim-shop.myshopify.com`, a tenant the attacker never controlled.

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
