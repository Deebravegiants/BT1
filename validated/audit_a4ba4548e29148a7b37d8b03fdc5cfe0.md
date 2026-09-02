### Title
Webhook `shop`, `topic`, and `webhook_id` fields are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so `Utils::HmacValidator.validate` verifies solely the integrity of the JSON body. The `shop`, `topic`, `webhook_id`, and `api_version` values — all read straight from unauthenticated HTTP headers — are never part of the signed payload, yet `Registry.process` trusts them and hands them to the app's handler as the identity of the originating shop.

### Finding Description
`Request#hmac` and `Request#to_signable_string` are defined as: [1](#0-0) 

`to_signable_string` returns only `@raw_body`: [2](#0-1) 

`shop`, `topic`, `webhook_id`, and `api_version` are read directly from HTTP headers with no cryptographic binding to the HMAC: [3](#0-2) 

`Registry.process` validates only the HMAC and then forwards these unverified header-derived fields straight to the app's handler as the authoritative identity of the webhook: [4](#0-3) 

The identity binding that should hold is: `shop header used by handler == shop bound by HMAC`. In practice: `shop header used by handler != any HMAC-covered value`, because the HMAC only covers the raw body bytes, not the header set.

### Impact Explanation
An unprivileged internet user who has installed the target app on their own shop (a normal, unprivileged action) receives genuine webhooks from Shopify: a raw JSON body plus a valid `X-Shopify-Hmac-Sha256` computed with the app's real `client_secret`. Because the signature covers only the body, the attacker can replay that exact body+HMAC pair to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) header to name a victim shop. `HmacValidator.validate` still succeeds (the body bytes are unchanged), so `Registry.process` calls the handler with `WebhookMetadata` claiming the data belongs to the victim shop. Any app that uses `shop` from the webhook payload as a tenant key (a pattern this library's own `WebhookMetadata` API encourages) will process, store, or act on attacker-controlled body content under a victim shop's identity — a cross-tenant data-integrity/spoofing issue.

### Likelihood Explanation
Requires only an unprivileged attacker who installs the app on their own shop to obtain a legitimately signed body/HMAC pair, then replays it with modified headers to the app's public webhook URL — no access token, `client_secret`, or privileged account is needed.

### Recommendation
Bind the header-derived identity fields (`shop`, `topic`, `webhook_id`, `api_version`) into the signed material, or otherwise cryptographically tie them to the HMAC-verified body (e.g., include them in `to_signable_string`, or independently verify `shop` against a value obtained through an authenticated channel such as a stored `access_token`/session lookup keyed by an integrity-checked identifier) before trusting them in `WebhookMetadata`.

### Proof of Concept
1. Attacker installs the vulnerable app on `attacker-shop.myshopify.com`; Shopify sends a real webhook: body `B`, header `X-Shopify-Hmac-Sha256: H` (valid for `B` under the app's `client_secret`), `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
2. Attacker resends the same `B`/`H` to the app's webhook endpoint but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `Utils::HmacValidator.validate` recomputes HMAC over `B` only and succeeds (`lib/shopify_api/webhooks/request.rb:35-38`, `lib/shopify_api/utils/hmac_validator.rb:26-31`).
4. `Registry.process` invokes the handler with `shop: "victim-shop.myshopify.com"` and the attacker-controlled body `B` (`lib/shopify_api/webhooks/registry.rb:188-200`), causing the app to act on forged data attributed to the victim tenant.

### Citations

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
