## Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then hands the handler a `shop` value that is read from an unauthenticated HTTP header. Because the `shop-domain` header is never included in the signed content, an attacker who can capture one valid `(body, hmac)` pair (e.g., from a webhook delivered to their own, legitimately installed test store) can replay that exact body/hmac while swapping the `x-shopify-shop-domain` header to any victim shop that also uses the app. The signature still validates, and the handler processes the payload as if it originated from the victim tenant.

### Finding Description
`Webhooks::Registry.process` performs identity/authenticity checks as follows: [1](#0-0) 

The HMAC check only validates `Utils::HmacValidator.validate(request)`, which in turn signs/verifies `request.to_signable_string`: [2](#0-1) 

`Webhooks::Request#to_signable_string` returns only the raw body — it does not include the shop, topic, or webhook-id headers: [3](#0-2) 

Meanwhile `shop` (along with `topic`, `webhook_id`, `api_version`) is read straight from HTTP headers with no cryptographic binding to the body or the HMAC: [4](#0-3) 

The `shop` value that the handler trusts for tenant attribution is taken directly from this unauthenticated field: [5](#0-4) 

This breaks the identity binding: `authenticated(hmac) == body` but `acted_on(handler.shop) == header`, and the header is not part of the signed content. Any shop using the same app shares the same `api_secret_key`/HMAC secret (`Context.api_secret_key`), so a genuine webhook received for shop A can be replayed verbatim against the app's webhook endpoint with the `shop-domain` header rewritten to shop B; the signature still checks out because the signature never covered the shop field in the first place.

### Impact Explanation
This is a cross-tenant confusion vector: an attacker who legitimately installs the app on their own shop (an unprivileged action available to anyone) receives real, validly-signed webhooks. By replaying the identical body+hmac with a forged `x-shopify-shop-domain` header pointing at a different (victim) shop, they can make the host application process attacker-controlled webhook data under the victim's tenant identity. Depending on how the host app's webhook handlers use `shop` (e.g., updating per-shop state, triggering per-shop side effects, or correlating orders/customers), this can lead to cross-tenant data corruption or privilege confusion — matching the "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is moderate-to-high for any app that has more than one merchant/shop installed, since:
- Any developer can install the app to their own shop and legitimately receive a validly-signed webhook to capture a `(raw_body, hmac)` pair.
- Webhook endpoints are internet-reachable and unauthenticated apart from the HMAC.
- No secret material is required — only observation of one's own legitimately delivered webhook.

### Recommendation
Include the `shop-domain` (and ideally `topic`/`webhook-id`/`api-version`) header values in the HMAC-signed content, e.g., by verifying against a canonical string that combines the headers with the body, rather than the raw body alone. At minimum, the shop identity used for handler dispatch must be cryptographically bound to what was verified by the HMAC signature.

### Proof of Concept
1. Install the vulnerable app on attacker-controlled shop `attacker.myshopify.com`; wait for (or trigger) a webhook delivery, capturing the raw JSON body `B` and the `x-shopify-hmac-sha256` header value `H` (both valid because they were genuinely signed for `attacker.myshopify.com`).
2. Send a POST request to the app's webhook endpoint with:
   - Body: the identical bytes `B`
   - `x-shopify-hmac-sha256`: `H` (unchanged)
   - `x-shopify-shop-domain`: `victim.myshopify.com` (a different shop that also has the app installed)
   - `x-shopify-topic`, `x-shopify-webhook-id`, `x-shopify-api-version`: reused/forged values as desired.
3. `Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC(secret, B) == H` — this passes because `B` and `H` are unchanged and match.
4. `Webhooks::Registry.process` builds `WebhookMetadata.new(shop: request.shop, ...)` using the attacker-forged `shop-domain` header (`lib/shopify_api/webhooks/registry.rb:198-199`), and invokes the host app's handler as if the webhook were authentically from `victim.myshopify.com`.

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

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```
