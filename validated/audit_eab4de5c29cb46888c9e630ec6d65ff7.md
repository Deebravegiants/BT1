## Title
Webhook `shop`, `topic`, and `webhook_id` fields are not covered by the HMAC signature, enabling cross-tenant webhook spoofing via signature replay - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, while the `shop`, `topic`, `webhook_id`, and `api_version` values that `Registry.process` uses to route and identify the merchant for a webhook are taken from separate, unauthenticated HTTP headers. An attacker who can obtain any body/HMAC pair that is valid for the shared `api_secret_key` (e.g. a webhook delivered for their own, attacker-controlled shop) can replay that exact body/HMAC to the app's webhook endpoint while substituting a different `shop-domain` (and/or `topic`) header. Because these header values are never part of the signed content, the signature still verifies, and the application will process the payload as if it originated from the spoofed shop/topic.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are read straight from headers with no cryptographic binding to the HMAC: [2](#0-1) 

`HmacValidator.validate` only checks the HMAC over `to_signable_string` (the raw body), so it never validates that the `shop`/`topic`/`webhook_id` headers are the ones Shopify actually associated with that HMAC: [3](#0-2) 

`Registry.process` trusts these unauthenticated headers to select the handler (`@registry[request.topic]`) and to build the `WebhookMetadata` passed to the app's handler, including `shop: request.shop`: [4](#0-3) 

The identity binding that should hold is: `shop authenticated by HMAC == shop acted upon by the handler`. Because `shop` (and `topic`/`webhook_id`) are excluded from the signed bytes, this equality is not enforced — only the JSON body bytes are bound to the HMAC, not the header-derived shop/topic identity that the handler uses to attribute and act on the data.

### Impact Explanation
This breaks the tenant boundary that webhook processing is supposed to enforce. An unprivileged user who has installed the app on any shop (including a free/attacker-controlled development store) can capture a legitimate, validly-signed webhook body for their own shop, then replay it against the app's public webhook endpoint with the `x-shopify-shop-domain` header changed to a victim merchant's domain (and/or the topic header changed to a different registered topic whose handler doesn't validate body shape). The HMAC still validates since it only covers the raw body. The receiving application will then process/store this attacker-supplied payload as if it were legitimate data from the victim shop, resulting in cross-tenant data injection/corruption in whatever the host application's webhook handler does with `WebhookMetadata#shop` (e.g., writing to the victim's tenant records, triggering tenant-scoped side effects under the wrong shop). This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
The attacker only needs the ability to install the app on a shop they control (or otherwise legitimately trigger a webhook delivery), capture the raw body and its valid `x-shopify-hmac-sha256` value, and issue an unauthenticated HTTP POST to the app's public webhook endpoint with modified `shop-domain`/`topic` headers — no access token, secret key, or privileged account is required. This is a straightforward replay, requiring no cryptographic break.

### Recommendation
Include `shop`, `topic`, and `webhook_id` (and any other header-derived fields used for routing/attribution) in the HMAC-signed content, or otherwise cryptographically bind them to the body before trusting them in `Registry.process`. At minimum, the library should document/require that consuming applications independently verify that `request.shop` matches an app-known, previously-registered shop for that specific delivery, rather than trusting the header value implicitly once the body-only HMAC passes.

### Proof of Concept
1. Install the app on attacker-controlled shop `evil.myshopify.com`; trigger any registered webhook topic (e.g. `orders/create`) so Shopify delivers a webhook with headers:
   - `x-shopify-hmac-sha256: <valid HMAC of raw body>`
   - `x-shopify-shop-domain: evil.myshopify.com`
   - `x-shopify-topic: orders/create`
   - raw body: `{...attacker-controlled order payload...}`
2. Capture the raw body and the `x-shopify-hmac-sha256` value (both are visible to the attacker as the receiving/controlling party of `evil.myshopify.com`).
3. Replay an HTTP POST directly to the app's public webhook endpoint with the same raw body and same `x-shopify-hmac-sha256`, but set `x-shopify-shop-domain: victim.myshopify.com`.
4. `Utils::HmacValidator.validate(request)` in `lib/shopify_api/webhooks/registry.rb:190` passes because it only checks the body's HMAC, and `Registry.process` invokes the handler with `shop: "victim.myshopify.com"` even though the payload actually originated from and was never associated with `victim.myshopify.com` by Shopify.

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
