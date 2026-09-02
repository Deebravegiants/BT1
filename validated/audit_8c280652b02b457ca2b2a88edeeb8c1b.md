I have enough evidence to make the determination now.

### Title
Webhook shop identity not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC signature over the raw request body only, while the `shop` attribute — which is trusted downstream to attribute the webhook payload to a specific merchant/tenant — is read from an unauthenticated HTTP header. This breaks the identity binding: `shop authenticated by HMAC != shop acted upon by the app`.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` verifies a webhook using `Utils::HmacValidator.validate(request)`, which delegates to `verifiable_query.to_signable_string` for the bytes it signs/verifies: [1](#0-0) 

`Request#to_signable_string` returns only `@raw_body`: [2](#0-1) 

But `Request#shop` is parsed from the `x-shopify-shop-domain` / `shopify-shop-domain` HTTP header, which is not part of the signed content at all: [3](#0-2) 

`HmacValidator.validate` only checks the HMAC over `to_signable_string` (the raw body), never binding it to the `shop` header: [4](#0-3) 

Finally, `Registry.process` passes the unauthenticated `request.shop` straight into `WebhookMetadata`, which is handed to the app's business-logic handler as the tenant identity for the payload: [1](#0-0) [5](#0-4) 

This is exactly the bug class described in the report: a field that is acted upon (`shop`, used to attribute/route the webhook data) is not covered by the cryptographic verification (HMAC over `raw_body` only). Critically, the webhook signing secret (`api_secret_key`/`client_secret`) is the **app's** single secret, shared across every shop that has installed the app — it is not shop-specific. Any merchant who installs the app receives legitimately-HMAC-signed webhooks for their own shop's events. Such a merchant is an "unprivileged" party with respect to any *other* tenant of the same app. They can capture one of their own genuine `(raw_body, hmac)` pairs and replay it to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header value (e.g., a victim shop's domain). Because the HMAC only covers `raw_body`, verification still succeeds, and the app processes the (attacker-chosen) body as if it originated from the victim shop.

### Impact Explanation
This crosses a tenant boundary: an unprivileged user of the app (any merchant who has installed it) can cause the host application to process attacker-supplied webhook data under a different shop's identity, since `Request#shop` is trusted by the handler but is not authenticated. This matches the Critical "cross-tenant access" impact category — the app cannot distinguish "data legitimately about shop A" from "data an installer of the app relabeled as belonging to shop B."

### Likelihood Explanation
The attack requires no access to the app's `api_secret_key`: only a legitimate webhook delivery to any single shop that has installed the app (something any merchant who installs the app can trivially obtain), plus the ability to send an HTTP request with a modified `x-shopify-shop-domain` header and the same raw body/HMAC pair to the app's public webhook endpoint. No credential theft or privileged access is required, and the codebase's own `Request` and `HmacValidator` implementation makes no attempt to bind `shop` to the signature.

### Recommendation
Include the shop domain (and ideally other Shopify-controlled identity headers) in the signable content used for HMAC verification, or otherwise independently verify that `request.shop` matches an expected/known session before trusting it in `WebhookMetadata`. At minimum, document and encourage host applications to cross-check the delivered shop against an existing, previously-established session/install record rather than trusting the header value outright.

### Proof of Concept
1. App is installed on `attacker.myshopify.com` and `victim.myshopify.com`, both webhooks signed with the same app-wide `api_secret_key`.
2. Attacker triggers an event on their own shop (e.g. `orders/create`) and captures the resulting webhook HTTP request, including `raw_body` and `x-shopify-hmac-sha256`.
3. Attacker POSTs the same `raw_body` and `x-shopify-hmac-sha256` to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses `shop` as `victim.myshopify.com` from the header (`lib/shopify_api/webhooks/request.rb:20-23`).
5. `Utils::HmacValidator.validate` recomputes the HMAC over `raw_body` only and it matches (`lib/shopify_api/utils/hmac_validator.rb:26-31`, `lib/shopify_api/webhooks/request.rb:35-38`), so the forged request passes verification.
6. `Registry.process` builds `WebhookMetadata.new(... shop: request.shop ...)` with `shop == "victim.myshopify.com"` and invokes the app's handler, which processes attacker-controlled data attributed to the victim tenant.

### Citations

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
