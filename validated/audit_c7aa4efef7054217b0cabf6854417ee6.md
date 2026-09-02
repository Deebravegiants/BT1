## Title
Webhook `shop` (tenant) identity is not covered by the HMAC signature, allowing cross-tenant webhook attribution — (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` (and `topic`, `webhook_id`, `api_version`) used to route and attribute an incoming webhook entirely from unauthenticated HTTP headers, while the HMAC signature that `Registry.process` verifies only covers the raw request body. This breaks the identity binding `shop-domain header == byte range covered by HMAC`, letting an attacker replay a validly-signed webhook body under a different shop's identity.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

but `shop` (and `topic`/`webhook_id`/`api_version`) are read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic binding to the signed payload: [2](#0-1) 

`Registry.process` validates the HMAC over the body only, then hands the header-derived `shop` straight to the application's webhook handler as the tenant identifier: [3](#0-2) 

`Utils::HmacValidator.validate` computes the signature from `verifiable_query.to_signable_string` (the raw body) and compares it to the `hmac` header — it never incorporates the `shop` header into the signed content: [4](#0-3) 

Because the `shop-domain` header sits outside the HMAC-covered bytes, an unprivileged actor who legitimately receives one correctly-signed webhook for their own shop (any Shopify merchant can install a public app and trigger a webhook for their own store) can capture the `raw_body` + valid `hmac` pair and resubmit the exact same HTTP request to the app's webhook endpoint with the `shopify-shop-domain` header rewritten to a victim shop's domain. `HmacValidator.validate` still succeeds (it only checks the body bytes), and `Registry.process` will invoke the handler with `WebhookMetadata.shop` set to the victim's domain — i.e., the equality the code implicitly assumes, `verified_bytes == attributed_identity`, does not hold.

This is the same bug class as the external report: a security-relevant field (there, the threshold-key/participant binding; here, the tenant `shop`) is acted upon by downstream logic without being covered by the cryptographic check that is supposed to authenticate the message.

### Impact Explanation
Any application built on this gem that uses `WebhookMetadata#shop` from `Registry.process` to key per-tenant side effects (e.g., "update shop X's local order record", "look up shop X's session/access token by this shop value") can be made to apply an attacker-supplied, differently-shop-tagged payload to another tenant's data path, since the shop attribution has no cryptographic guarantee. This crosses a tenant boundary using only a legitimately-obtained webhook from the attacker's own store, satisfying the "cross-tenant access" high/critical impact bar.

### Likelihood Explanation
Likelihood is moderate-to-high for any app that trusts `WebhookMetadata.shop` without independently verifying it (which the gem's own API does not require or provide): the attacker only needs to operate a real Shopify shop (installable by anyone) to obtain one legitimately-signed webhook, then replay it with a modified `shop-domain` header — no access to the app's `client_secret` or a merchant's access token is required.

### Recommendation
Include the shop domain (and preferably the webhook id / topic) as part of the HMAC-signed material verified in `Utils::HmacValidator.validate`/`Webhooks::Request#to_signable_string`, or otherwise cryptographically bind the `shop-domain` header to the signed payload before it is trusted as the webhook's tenant identity, mirroring the recommendation in the referenced report (verify that the identity used downstream matches the identity actually authenticated).

### Proof of Concept
1. Install the target app on an attacker-controlled shop `attacker.myshopify.com`; trigger any webhook so Shopify sends a validly HMAC-signed request: body `B`, header `shopify-hmac-sha256: H` (valid for `B`), `shopify-shop-domain: attacker.myshopify.com`.
2. Replay this exact request to the app's webhook endpoint, changing only the header to `shopify-shop-domain: victim.myshopify.com`, keeping body `B` and `hmac H` unchanged.
3. `Utils::HmacValidator.validate` recomputes HMAC over `B` only (see `to_signable_string`), matches `H`, and passes.
4. `Registry.process` invokes the handler with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)`, causing the app to process attacker-controlled webhook content as if it originated from the victim shop. [3](#0-2)

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
