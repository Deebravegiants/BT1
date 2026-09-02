### Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` authenticates an inbound webhook by HMAC-validating only the raw request body, but the `shop` identity that the app's `WebhookHandler` uses to route/attribute the event to a tenant is read from an unauthenticated header. This breaks the identity binding `hmac_verified_bytes == acted_on_identity`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`ShopifyAPI::Utils::HmacValidator.validate` computes the signature strictly over `verifiable_query.to_signable_string` (i.e., the body) and compares it to the `hmac` supplied by the request: [2](#0-1) 

However, `Request#shop` is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is not part of the signed material: [3](#0-2) 

`Webhooks::Registry.process` validates the HMAC (over the body only) and then immediately trusts `request.shop` as the tenant identity, passing it into `WebhookMetadata` for the app-supplied handler to act on: [4](#0-3) [5](#0-4) 

This is the exact bug class described in the external report: the code validates one field (the body, via HMAC) but acts on a different, unvalidated field (`shop`) to make a security decision (tenant attribution) — analogous to checking `msg.sender`'s counter while deleting `_user`'s counter. Because the HMAC is computed only from `secret + raw_body`, it is independent of which shop originated the request. Any two webhooks—one from the attacker's own shop and one destined for a victim shop—that happen to carry identical bodies (which is common for many topics: `app/uninstalled`, `shop/redact`, low-cardinality body variants, or a body an attacker fully controls by triggering an action that produces a known payload on their own shop) will produce the same valid `hmac` value. An attacker who legitimately installs the app on their own shop receives a genuine `(body, hmac)` pair signed by Shopify with the app's real secret. They can then replay that exact `(body, hmac)` pair to the app's webhook endpoint while substituting the `shop-domain` header with a victim shop's domain. `HmacValidator.validate` still succeeds (it never inspected `shop`), and the app's handler receives `WebhookMetadata(shop: "victim-shop.myshopify.com", ...)`, causing it to process/store attacker-controlled data attributed to another tenant.

### Impact Explanation
This falls under "Critical – cross-tenant access." An unprivileged user who merely installs the app on their own (attacker-controlled) shop can forge webhook events that the library validates as authentic for an arbitrary victim shop, without ever needing the app's `client_secret`, an access token, or any privileged account — they only need a shop of their own on which the app is installed (the normal, unprivileged onboarding path for any merchant). Any host application relying on this gem's HMAC validation plus `request.shop`/`WebhookMetadata#shop` to scope data per tenant is exposed to cross-tenant data injection or corruption.

### Likelihood Explanation
High. The only precondition is installing the app on a shop the attacker controls (a normal, unauthenticated/self-service action for public apps) and capturing one legitimately signed webhook whose body is attacker-predictable or reproducible (many topics have static or attacker-triggerable bodies, e.g., `app/uninstalled`, GDPR/redact topics, or webhooks with generic minimal payloads). No cryptographic secret needs to be recovered; the valid `(body, hmac)` pair is handed to the attacker directly by Shopify for their own shop.

### Recommendation
Bind the shop identity into the authenticated material before trusting it:
- Include the `shop-domain` (and ideally `topic`/`webhook-id`) header values in the HMAC-covered signable string in `Request#to_signable_string`, or
- Have `Registry.process` cross-check `request.shop` against an independently-verified source of truth (e.g., require callers to pass the expected shop and assert equality) before constructing `WebhookMetadata`, rather than trusting the header verbatim.
- Document clearly that `WebhookMetadata#shop` is not covered by the HMAC today, so host apps do not use it alone for tenant scoping without additional verification.

### Proof of Concept
1. Install the app on `attacker-shop.myshopify.com` (unprivileged, self-service).
2. Trigger a webhook topic with a fixed/predictable body (e.g., `app/uninstalled`), capturing the real request Shopify sends, including its valid `X-Shopify-Hmac-SHA256` header computed by Shopify with the app's real secret over that body.
3. Replay the exact same raw body and `X-Shopify-Hmac-SHA256` value to the app's webhook endpoint, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`:
   - `validate_signature` recomputes `HMAC(secret, raw_body)` and compares to the header — it matches, since `shop` was never part of the signed string (`lib/shopify_api/webhooks/request.rb:35-38`, `lib/shopify_api/utils/hmac_validator.rb:26-31`).
5. `Registry.process` proceeds to call the registered `WebhookHandler#handle` with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`), even though the request never actually originated from Shopify on behalf of that victim shop.

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
