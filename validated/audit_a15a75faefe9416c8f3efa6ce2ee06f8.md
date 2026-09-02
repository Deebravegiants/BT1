### Title
Webhook HMAC only signs the raw body, so `shop`, `topic`, and `webhook_id` are unauthenticated attacker-controlled headers, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw request body only, while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from HTTP headers that are never included in the signed content. `Registry.process` validates only the body HMAC and then trusts these unauthenticated header values to dispatch the webhook to the tenant-specific handler. This breaks the intended binding `hmac == HMAC(secret, shop || topic || body)` down to `hmac == HMAC(secret, body)`, letting an attacker with any one legitimately-signed webhook body replay it with a forged `shop-domain`/`topic` header to impersonate a different merchant.

### Finding Description
`to_signable_string` for `Webhooks::Request` returns only `@raw_body`: [1](#0-0) 

Meanwhile, `shop`, `topic`, `webhook_id`, and `api_version` are parsed directly from headers without any cryptographic binding to the signature: [2](#0-1) 

`HmacValidator.validate` computes the signature strictly over `verifiable_query.to_signable_string` (i.e., the raw body) and compares it to the `hmac` header: [3](#0-2) 

`Registry.process` performs this body-only HMAC check and then unconditionally trusts `request.shop` and `request.topic` to route and construct `WebhookMetadata` for the handler: [4](#0-3) 

The intended security property is that a webhook's tenant identity (`shop`) and semantic meaning (`topic`) are authenticated together with its payload — i.e. `hmac == HMAC(secret, shop || topic || body)`. In this implementation, the check reduces to `hmac == HMAC(secret, body)`, with `shop` and `topic` supplied out-of-band and unauthenticated. This is exactly the "field acted on but not covered by the HMAC" identity-binding break: the `shop` field host applications use as their session/tenant key is not cryptographically tied to the signature that is supposed to authenticate the whole webhook.

Because Shopify's webhook endpoints are plain public HTTP(S) endpoints operated by the app developer, any unprivileged internet user can POST directly to them (this is not host-application misuse; it's the documented, expected entry point this gem processes). An attacker who has ever received one legitimate webhook (e.g., by installing the app on a free/trial store they control, and triggering any webhook topic that is registered) possesses a `(raw_body, hmac)` pair valid under the app's real secret. Since headers are excluded from the signature, the attacker can resend that exact `(raw_body, hmac)` pair while substituting the `shop-domain` header for any target merchant's shop and/or the `topic` header for any other registered topic, and `Utils::HmacValidator.validate` will still accept it.

### Impact Explanation
This enables cross-tenant confusion: the host application's webhook handler receives `WebhookMetadata` where `shop` names an arbitrary victim merchant chosen by the attacker, while `body`/`topic` are attacker-influenced (limited to content the attacker could legitimately generate for their own store, but freely re-labeled to any topic/shop). Depending on how the host app uses `data.shop` (e.g., to look up the merchant's session, to trigger data updates, uninstalls, or GDPR-style deletions keyed by shop), this can cause cross-tenant actions to be performed against a shop the attacker does not control — satisfying the "cross-tenant access" Critical-impact bucket, since the shop identity used to route sensitive per-tenant webhook processing is forgeable by anyone who has ever received one valid webhook from Shopify for their own store.

### Likelihood Explanation
Reasonably likely: the attacker needs no privileged credentials, access token, or `api_secret_key` — only a free/dev Shopify store with the target app installed, which is trivial to obtain, plus network access to POST to the app's public webhook endpoint (both requirements are consistent with an "unprivileged internet user"). The gem itself performs no correlation between the signed body and the headers it exposes as `shop`/`topic`/`webhook_id`, so any host app that follows this gem's documented `Registry.process` flow inherits the gap.

### Recommendation
Bind the tenant/topic identity into the authenticated content, or otherwise cryptographically tie the header-derived values to the request before trusting them:
- Include `shop`, `topic`, and `webhook_id` in the string that `to_signable_string` returns (if Shopify's actual HMAC scheme permits extending the signed payload), or
- At minimum, cross-check that the `shop` value in the parsed body (where available) matches the header-derived `shop`, and reject mismatches, and
- Document/enforce that host applications must not use `request.shop` alone as an authorization boundary without an additional server-side registration check (e.g., verifying the shop is one that legitimately installed the app and is expected to receive this topic) before this value is treated as authenticated.

### Proof of Concept
1. Attacker installs the target app on their own (free/dev) Shopify store and triggers a registered webhook topic (e.g. `orders/create`), causing Shopify to deliver a legitimately HMAC-signed webhook to the app's endpoint:
   ```
   POST /webhooks
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: <valid_hmac_for_body>
   X-Shopify-Shop-Domain: attacker-shop.myshopify.com
   X-Shopify-Webhook-Id: <id>
   Body: {"id": 1, ...attacker-controlled order data...}
   ```
2. Attacker captures this raw body and its valid `X-Shopify-Hmac-Sha256` value.
3. Attacker resends the identical body and HMAC header to the same endpoint, but replaces:
   ```
   X-Shopify-Shop-Domain: victim-shop.myshopify.com
   ```
   (optionally also changing `X-Shopify-Topic` to another topic registered by the app).
4. `Webhooks::Request.new` accepts the headers, and `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `HMAC(secret, raw_body)` — unaffected by the header changes: [5](#0-4) 
5. The handler is invoked with `WebhookMetadata.new(topic: request.topic, shop: "victim-shop.myshopify.com", body: request.parsed_body, ...)`, causing the host application to process a spoofed cross-tenant webhook as if it genuinely originated from `victim-shop.myshopify.com`. [6](#0-5)

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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
