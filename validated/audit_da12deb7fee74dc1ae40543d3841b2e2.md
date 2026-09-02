### Title
Webhook shop-domain header is not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by verifying the HMAC over the raw request body, then blindly trusts the unauthenticated `shop-domain` header when building the `WebhookMetadata` passed to the app's handler. Because the HMAC is computed with the app's single shared `api_secret_key` (identical for every merchant using the app) and only covers the body bytes, any party who can obtain one validly-signed webhook payload (e.g., by installing the app on their own store) can replay that exact body+HMAC pair while substituting the `shop-domain` header for a victim shop, and the gem will report the request as authentic and attribute it to the victim.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`HmacValidator.validate` computes the signature purely from `to_signable_string` (the body) and the app's `api_secret_key`, comparing it to the `hmac` header: [2](#0-1) 

`Registry.process` uses this HMAC check as the sole authenticity gate, then constructs `WebhookMetadata` directly from `request.shop`, which is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header — a value never included in the signed material: [3](#0-2) [4](#0-3) 

The broken identity binding, stated as an equality that the code assumes but never enforces:
`shop_domain_header == shop_that_the_signed_body_actually_belongs_to`

Because the `api_secret_key` is a single app-level secret (not per-tenant), a valid HMAC only proves "this body was signed by this app's secret" — it proves nothing about which merchant the body/header pair originated from. Any unprivileged actor who installs the target app on their own store receives their own legitimately-signed webhooks (valid body + valid HMAC for that secret). They can capture such a payload and re-POST it to the app's webhook endpoint with the `shop-domain` header rewritten to any other merchant's `myshopify.com` domain. `HmacValidator.validate` still returns `true` (the body/HMAC pair is unmodified and correctly signed), and `Registry.process` forwards `shop: <attacker-chosen domain>` to the host application's handler as authenticated data.

### Impact Explanation
This crosses a tenant boundary: the gem hands the host application webhook data tagged with an arbitrary, attacker-controlled shop identity while claiming it passed authenticity/HMAC verification. Any host application that keys behavior (e.g., which merchant's records to update/delete, which session/access token to use for follow-up API calls, billing/inventory sync, GDPR data-erasure webhooks, etc.) off `WebhookMetadata#shop` as returned by this gem will act on the wrong tenant's data in response to attacker-supplied input, i.e., cross-tenant access enabled by the library's own trust decision.

### Likelihood Explanation
Exploitability only requires the attacker to be able to install the target app on any shop they control (a routine, unprivileged action for any Shopify Partner/dev store) to obtain one valid signed webhook body, then replay it with a modified header to the same app's public webhook endpoint. No access token, `api_secret_key`, or victim credentials are needed — the whole point is that the shared secret and the per-tenant identity are decoupled by this code path.

### Recommendation
- Do not treat `request.shop` as trusted/authenticated data merely because `HmacValidator.validate(request)` returned true.
- Bind the shop identity into the verified material: either include the `shop-domain` header in the signable string used for HMAC comparison, or require callers to independently verify `request.shop` against a known/expected shop (e.g., the session under which the webhook was registered) before acting on `WebhookMetadata`.
- At minimum, document prominently in `Registry.process`/`WebhookMetadata` that `shop` is unauthenticated header data and must not be used as a tenant-selection key without additional verification.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and receives a legitimate webhook, e.g.:
   ```
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <valid-hmac-for-body>
   x-shopify-shop-domain: attacker-shop.myshopify.com
   Body: {"id":123, ...}
   ```
2. Attacker replays the identical body and `hmac-sha256` value to the same endpoint, changing only the shop header:
   ```
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <same-valid-hmac>
   x-shopify-shop-domain: victim-shop.myshopify.com
   Body: {"id":123, ...}
   ```
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)` which returns `true` (body unchanged, HMAC computed only over body with the shared `api_secret_key`).
4. `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: ..., ...)` is passed to the app's handler as if it were an authentic webhook for `victim-shop.myshopify.com`.

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
