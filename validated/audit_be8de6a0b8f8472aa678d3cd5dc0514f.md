### Title
Webhook shop-domain tenant identifier is not covered by the HMAC signature, allowing cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely via `Utils::HmacValidator.validate(request)`, which validates the HMAC over `request.to_signable_string`. That signable string is defined as only the raw request body (`@raw_body`), never the `shop-domain` header. Yet the `shop` value handed to the app's webhook handler — used to identify which tenant the event belongs to — is read directly from the unauthenticated `shopify-shop-domain` / `x-shopify-shop-domain` header. This breaks the intended binding between "the bytes Shopify signed" and "the tenant the app believes sent the event."

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns `@raw_body` only: [1](#0-0) 

`Request#shop` is derived independently from a plain HTTP header that is never included in the signed payload: [2](#0-1) 

`Registry.process` validates the HMAC and then dispatches to the handler using `request.shop` as the tenant identifier, with no additional check that the body content actually corresponds to that shop: [3](#0-2) 

`HmacValidator.validate` performs a constant-time comparison of the computed signature against `verifiable_query.hmac`, but the signature is only ever computed from `to_signable_string` (i.e., the raw body), never from the shop header: [4](#0-3) 

**The broken identity binding, stated as an equality that the gem fails to enforce:**
`shop-domain-covered-by-hmac == shop-domain-header-trusted-by-handler`

In reality: `HMAC(secret, raw_body)` authenticates only the body; `request.shop` (the header) is unauthenticated and can be freely modified in transit or by any actor capable of constructing an HTTP request with a valid `(raw_body, hmac)` pair.

An attacker who owns/operates any shop that has installed the app can receive genuine Shopify-signed webhooks (correct `raw_body` + `hmac`) for that shop. Because `hmac` never binds to `shop-domain`, the attacker can replay that exact `raw_body`/`hmac` pair to the app's webhook endpoint while substituting the `shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` will still pass (it only checks the body against the secret), and `Registry.process` will invoke the handler with `WebhookMetadata` claiming the event is `shop: <victim-shop>`.

### Impact Explanation
This is a cross-tenant identity-binding failure: an app relying on this gem's webhook processing to key session/data lookups, revoke tokens, or perform GDPR-mandated actions (`shop/redact`, `customers/redact`, `customers/data_request`) by `request.shop` can be tricked into acting on behalf of a shop that never actually sent the webhook. Depending on the handler's logic this can cause cross-tenant data manipulation, incorrect access-token revocation for another merchant, or forged compliance/redaction actions attributed to an uninvolved shop — matching the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Exploitation requires the attacker to have access to at least one valid `(raw_body, hmac)` pair signed with the app's `client_secret` — obtainable by installing the app on an attacker-controlled development/test store and capturing its own genuine webhook deliveries (topics like `app/uninstalled`, `shop/redact`, or any topic whose body doesn't inherently reveal/bind to the sending shop). No possession of the app's `client_secret` or a leaked access token is needed; only the ability to send an HTTP request to the app's public webhook endpoint with attacker-controlled headers. Likelihood is moderate-to-high for any integrator who trusts `WebhookMetadata#shop` as the sole tenant identifier, which the gem's own documentation and API surface encourage.

### Recommendation
Bind the shop identity into the value that is actually authenticated:
- Include the `shopify-shop-domain` header (and ideally `topic`, `webhook-id`, `api-version`) in the HMAC-signable content used by `to_signable_string`, so tampering with the header invalidates the signature, or
- Cross-check the shop domain against externally stored/expected state (e.g., verify `request.shop` corresponds to a known, previously authorized session) before dispatching to a handler, rather than trusting the header value implicitly.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com`, causing Shopify to send a legitimate webhook (e.g., `app/uninstalled`) to the app's registered endpoint with a valid `raw_body` and `x-shopify-hmac-sha256` computed with the shared `client_secret`.
2. Attacker captures this `(raw_body, hmac)` pair.
3. Attacker crafts a new HTTP POST to the same webhook endpoint using the identical `raw_body` and `hmac` header, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses this into a `Request` whose `shop` returns `"victim-shop.myshopify.com"` [2](#0-1) , while `to_signable_string` still returns the original, still-valid `raw_body` [1](#0-0) .
5. `Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which succeeds because the body/hmac pair is genuinely valid [5](#0-4) .
6. The registered handler is invoked with `WebhookMetadata` claiming `shop: "victim-shop.myshopify.com"` [6](#0-5) , causing the app to act as though the event originated from the victim's shop even though it never did.

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
