### Title
Webhook `shop-domain` (and `topic`/`webhook-id`) Trusted Without HMAC Binding, Enabling Cross-Tenant Webhook Replay - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by HMAC-validating the raw request body, then unconditionally trusts the `shop-domain` header taken from the same (unauthenticated) HTTP headers to identify which tenant/shop the payload belongs to. Because the signable string only covers the body, the shop identity is never cryptographically bound to the signature, breaking the identity binding `hmac_valid(body) == shop_is_authentic`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` accessors read directly from HTTP headers that are never included in the HMAC-signed content: [2](#0-1) 

`Registry.process` validates the HMAC (which only proves the *body* bytes were signed with `api_secret_key`) and then immediately trusts `request.shop` as the tenant identity passed into the handler: [3](#0-2) 

`Utils::HmacValidator.validate` confirms this: it only recomputes and compares the signature over `verifiable_query.to_signable_string`, i.e., the body for webhooks: [4](#0-3) 

The resulting `WebhookMetadata.shop` field, which app code is expected to use to scope the handled event to a tenant, is populated straight from the unauthenticated header: [5](#0-4) 

This is the exact bug class described in the external analog report: an identity field (there, `lastDepositTime`; here, the shop identity) is acted upon by a security-relevant code path (there, bonus eligibility; here, tenant attribution) without being covered by the binding mechanism that is supposed to guarantee its authenticity (there, the cadence/claim check; here, the HMAC). The equality that should hold — `hmac_valid(raw_body) ⇒ shop_header_is_authentic` — does not hold, because `shop_header` is outside the signed scope.

### Impact Explanation
Any actor who can observe or replay one legitimately-signed webhook body/HMAC pair (e.g., their own shop's webhook, which Shopify delivers to the app's public endpoint over plain HTTP semantics with no mutual auth on this header) can resend the identical `raw_body`/`hmac-sha256` pair to the app's webhook endpoint while substituting an arbitrary `shop-domain` header. `HmacValidator.validate` will still pass because the signature never covered the shop header, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload originated from a different shop. Any host application that uses `data.shop` for tenant-scoped side effects (e.g. GDPR `customers/redact`, `shop/redact`, or business logic keyed off `shop`) can be made to act on/attribute data to a shop the attacker does not own — a cross-tenant confusion/cross-tenant access issue, which matches the "Critical – cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is moderate-to-high for any app that dispatches per-tenant logic from `WebhookMetadata#shop` without independently verifying the shop against a known/expected value (e.g., cross-checking against the session store for that endpoint). No secrets, TLS interception, or privileged access are required — only capture/replay of one's own or any previously observed valid webhook delivery, which the gem's public API documents as the accepted shape of `Request`.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the value verified against the HMAC (or, if Shopify's wire format cannot be changed, have `Registry.process`/`WebhookMetadata` cross-validate the `shop-domain` header against an independently trusted source — e.g., require the caller to supply the expected shop and assert equality — before dispatching to handlers). At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated and must not be used for tenant-security decisions without additional verification.

### Proof of Concept
1. App receives a legitimate webhook for `shop-a.myshopify.com`: headers `x-shopify-shop-domain: shop-a.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC of raw_body>`, body `raw_body`.
2. Attacker (who owns `shop-a` or otherwise obtained this delivery) resends the exact same `raw_body` and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but sets `x-shopify-shop-domain: shop-victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` accepts the headers/body (all required headers present).
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because `to_signable_string` only checks `raw_body`, unaffected by the swapped `shop-domain` header (`lib/shopify_api/webhooks/request.rb:35-38`, `lib/shopify_api/utils/hmac_validator.rb:12-31`).
5. The registered handler receives `WebhookMetadata.new(shop: "shop-victim.myshopify.com", ...)` and, if it trusts `data.shop` for tenant-scoped effects, performs an action attributed to `shop-victim` that the attacker never authorized.

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
