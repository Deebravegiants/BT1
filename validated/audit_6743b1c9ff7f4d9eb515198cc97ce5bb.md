### Title
Webhook `shop` identity is trusted without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` exposes a `shop` accessor sourced directly from the unauthenticated `X-Shopify-Shop-Domain` / `shopify-shop-domain` HTTP header, while `Utils::HmacValidator.validate` only verifies the HMAC over the raw request body (`to_signable_string` returns `@raw_body`). `Registry.process` passes this unauthenticated `shop` value straight to the host application's webhook handler as the tenant identifier, so the equality the app relies on — "the shop that produced a validly-signed body" == "the shop the handler is told this event belongs to" — is never actually checked.

### Finding Description
`Request#hmac` reads the signature from the header, and `Request#to_signable_string` (the value that gets HMAC-verified) is just the raw body: [1](#0-0) 

`Request#shop`, by contrast, is read straight from a header that is never included in the signed payload: [2](#0-1) 

`HmacValidator.validate`/`validate_signature` verifies only `verifiable_query.to_signable_string` (the body) against the secret; it has no knowledge of, and does not bind, the `shop` header at all: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately forwards the unauthenticated `request.shop` value to the handler as the tenant/shop identity for the event: [4](#0-3) 

Because the same `api_secret_key` is shared by every shop that installs a given app, and the signature only covers the body (not the shop header), any merchant who installs the app on their own store can obtain a genuinely-signed webhook (valid `hmac` for a body they fully control, e.g. by triggering an `orders/create` event on their own shop). They can then replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. `HmacValidator.validate` still returns `true` (only the body is checked), and `Registry.process` hands the handler a `WebhookMetadata` object whose `shop` is the attacker-chosen victim domain, with the attacker-supplied body content, e.g.: [5](#0-4) 

The identity binding broken here is: **shop that cryptographically produced the payload == shop the handler is told owns the payload**. This binding does not hold, since `shop` is not part of the HMAC-signed material.

### Impact Explanation
This breaks tenant isolation (cross-tenant access): the gem lets an attacker who legitimately controls their own installed shop inject arbitrary webhook content and have the host application process it under a different, victim shop's identity. Any downstream logic that uses `WebhookMetadata#shop` to look up per-tenant sessions, apply per-tenant business logic, or write to per-tenant storage will act on the victim tenant using attacker-controlled data — a cross-tenant data integrity/confidentiality violation.

### Likelihood Explanation
Likelihood is Medium-to-High for any app that: (1) allows self-service installs (most public/embedded apps do), so the attacker can obtain a validly-signed body/HMAC pair for their own shop trivially, and (2) uses `WebhookMetadata#shop` as a tenant key when handling the webhook (the documented/intended usage pattern). No access token, `api_secret_key`, or privileged account is required — only the ability to install the app on an attacker-controlled/free development store and send a crafted HTTP request to the app's public webhook endpoint.

### Recommendation
Do not trust the `shop`/`X-Shopify-Shop-Domain` header as an authenticated identity. Either:
- Include the shop domain in the HMAC-signed material used for verification (not possible unilaterally since Shopify controls what it signs), or
- Cross-check `request.shop` against an identity actually bound to the signature/subscription (e.g., resolve the shop from a per-shop webhook secret/subscription id fetched independently, or verify the shop against Shopify via an authenticated API call) before dispatching to handlers, rather than trusting the header value directly once the body-only HMAC passes.
- At minimum, document prominently that `WebhookMetadata#shop` is not cryptographically authenticated and must not be used as a sole tenant-scoping key without additional verification.

### Proof of Concept
1. Attacker installs the target app on their own development shop `attacker.myshopify.com`, obtaining a genuine webhook delivery for, e.g., `orders/create` with body `B` and a valid `hmac` computed with the app's shared `api_secret_key`.
2. Attacker resends the exact same raw body `B` and `hmac` header to the app's public webhook endpoint, but replaces `X-Shopify-Shop-Domain: attacker.myshopify.com` with `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` accepts the request (all required headers present).
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only recomputes HMAC over `raw_body` [6](#0-5) .
5. The handler receives `WebhookMetadata.new(topic:, shop: "victim.myshopify.com", body: <attacker-controlled>, ...)` [5](#0-4) , and any tenant-scoped processing keyed off `shop` now operates on the victim tenant using attacker-supplied data.

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
