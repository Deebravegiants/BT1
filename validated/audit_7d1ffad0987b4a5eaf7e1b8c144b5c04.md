### Title
Webhook `shop-domain` header is trusted for tenant attribution but not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable content solely from the raw HTTP body (`to_signable_string` returns `@raw_body`), while the `shop`, `topic`, `api_version`, and `webhook_id` fields are all read directly from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` validates only the body-HMAC and then dispatches to the app's handler using the header-derived `shop` value, without any check that the header's `shop` actually matches the tenant the signed body was generated for.

### Finding Description
`Utils::HmacValidator.validate` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it to `verifiable_query.hmac`: [1](#0-0) 

For webhooks, `to_signable_string` is defined as just the raw body, and `hmac` is parsed from the `X-Shopify-Hmac-Sha256` header. Critically, `shop`, `topic`, `api_version`, and `webhook_id` are read from separate, unsigned headers: [2](#0-1) 

`Registry.process` validates only this body-bound HMAC and then passes the header-derived `shop` straight to the app's handler as the tenant identity for the webhook payload: [3](#0-2) 

The identity binding that should hold is:
`hmac_valid(body) == true` should imply `shop_claimed_in_header == shop_the_body_was_actually_signed_for`.

In this implementation that equality does not hold: the HMAC only proves the body bytes were signed by Shopify using the app's `client_secret` (i.e., "this body was produced for *some* shop calling this app"), it says nothing about which shop's header the body is delivered under. Any party who has one valid `(raw_body, X-Shopify-Hmac-Sha256)` pair for the app - e.g. a real merchant who installed the app and receives legitimate webhook deliveries for their own store - can replay that exact body+HMAC to the app's webhook endpoint while substituting an arbitrary value in `X-Shopify-Shop-Domain` (and `webhook-id`/`topic`, if desired to fit the target's expected schema). The signature check still passes because it only recomputes the HMAC over `@raw_body`, and the handler will process the payload as if it belongs to the spoofed shop.

### Impact Explanation
This allows cross-tenant data injection: an attacker with a legitimate app installation on shop A can cause the app to process attacker-controlled webhook data attributed to shop B (any known/guessed `myshopify.com` domain), because the header used to select which tenant's data store the payload updates is never bound to the signed content. Depending on what the host app does with `WebhookMetadata#shop` (e.g., look up records, update inventory/orders, sync data) this is a cross-tenant integrity/confidentiality issue for downstream data. This matches the report's category of "a field acted on but not covered by the HMAC."

### Likelihood Explanation
Any user who can install the app on a shop they control can trivially capture one valid webhook delivery (body + HMAC) from their own store via a proxy/logging endpoint, then replay it against the app's public webhook URL with a forged `X-Shopify-Shop-Domain` header. No access to `client_secret`, access tokens, or Shopify infrastructure is required — only a normal, unprivileged merchant installation, which is the exact "unprivileged internet user" threat model in scope.

### Recommendation
Bind the shop (and ideally topic/webhook_id) into the value that is HMAC-verified, or otherwise cross-check the header-derived shop against a value obtained through an authenticated channel:
- Include the `shop-domain` header (and other operationally significant headers) in the signable string used by `HmacValidator`, matching it against a mirrored signature Shopify includes, OR
- Require host apps to verify `request.shop` against a known/expected shop for the delivery (e.g., validate that the shop is one that has completed OAuth/installed the app and that no other currently-valid webhook subscription for a different shop maps to the same raw body/HMAC), OR
- At minimum, document explicitly in `lib/shopify_api/webhooks/registry.rb` / `request.rb` that `shop` is unauthenticated and must not be used as the sole tenant-scoping key without additional verification, and provide a built-in replay/binding check (e.g. binding webhook_id to a previously-registered subscription's shop).

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and configures a webhook subscription (e.g. `orders/create`) that is delivered to the app's webhook endpoint.
2. Attacker intercepts one legitimate delivery, capturing:
   - Raw body `B`
   - Header `X-Shopify-Hmac-Sha256: H` (valid because Shopify signed `B` with the app's `client_secret`)
3. Attacker sends a new POST to the same webhook endpoint with:
   - Body: `B` (unchanged)
   - `X-Shopify-Hmac-Sha256: H` (unchanged, still valid because HMAC is computed only over `B`)
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (forged)
   - `X-Shopify-Topic`, `X-Shopify-Webhook-Id` adjusted as desired.
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)` is constructed; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because `to_signable_string` only inspects `B`: [4](#0-3) 
5. The handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)` and processes attacker-controlled data as if it belonged to `victim-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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
