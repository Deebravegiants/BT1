I have sufficient evidence to make a determination on this analog.

### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` extracts the tenant identifier (`shop-domain` header) completely outside the scope of the HMAC signature check, and `Registry.process` passes that unauthenticated value straight into the handler as the trusted `shop` for the webhook event.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body: `@raw_body`, with no incorporation of the `shop-domain`, `topic`, `webhook-id`, or `api-version` headers. [1](#0-0) 

`ShopifyAPI::Utils::HmacValidator.validate` computes/compares the signature solely against `verifiable_query.to_signable_string`, i.e. the body only: [2](#0-1) 

`Registry.process` treats a body whose HMAC validates as fully authenticated, then builds `WebhookMetadata` directly from `request.shop` (the raw, unauthenticated `shop-domain`/`x-shopify-shop-domain` header) without any cross-check against the shop that was actually used to register/verify the webhook subscription: [3](#0-2) [4](#0-3) 

The identity binding that should hold is: `shop value the app acts on == shop value cryptographically bound to the signed payload`. Instead the code only proves `hmac == HMAC(api_secret_key, body)`; it never proves `shop-domain header == shop that the secret/body actually belongs to`. Because Shopify webhooks for a given app are all signed with the **same** `api_secret_key` regardless of which installed shop sent them, any shop that has legitimately installed the app can capture a genuine `(body, hmac)` pair from its own webhook deliveries and replay it to the app's webhook endpoint with a forged `X-Shopify-Shop-Domain` header naming a different, victim shop. `HmacValidator.validate` will pass (the body/hmac pair is genuinely valid for the shared secret), and `Registry.process` will hand the handler a `WebhookMetadata` claiming the event came from the victim shop.

### Impact Explanation
This breaks the shop/tenant identity binding without needing the victim's access token or any privileged access — merely installing the app on an attacker-controlled shop is enough to obtain valid `(body, hmac)` pairs. Downstream app code that trusts `WebhookMetadata#shop` to scope database writes, GDPR-style redactions, order/customer state changes, or entitlement lookups can be tricked into applying attacker-supplied data or actions under a different tenant's identity — a cross-tenant access condition.

### Likelihood Explanation
The attacker only needs to be a legitimate (even free/trial) installer of the target app to receive real webhook deliveries signed with the app's shared secret, then can replay that exact HTTP body/HMAC pair against the app's public webhook endpoint with a modified shop header. No secret, token, or privileged access is required — only knowledge of a genuine delivery and control of outbound HTTP headers, which any unprivileged internet user/app-installer has.

### Recommendation
Do not trust the `shop-domain` header purely because the body-only HMAC validates. Either include the shop domain/webhook id inside the HMAC-signed content, or require callers of `Registry.process`/`WebhookHandler#handle` to cross-verify `request.shop` against the shop associated with the session/subscription that registered the given `topic`/`webhook_id`, rejecting mismatches before invoking the handler.

### Proof of Concept
1. Install the target app on an attacker-controlled shop `attacker.myshopify.com`; the app registers a webhook (e.g. `orders/create`) for that shop.
2. Trigger the event so Shopify delivers a genuine webhook to the app's endpoint: body `B`, header `X-Shopify-Hmac-Sha256: H` (valid since `H = HMAC(api_secret_key, B)`), and `X-Shopify-Shop-Domain: attacker.myshopify.com`.
3. Attacker replays the exact same request to the same endpoint, but rewrites the header to `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses this into a `Request` whose `hmac` and `to_signable_string` (raw body) are unchanged; `HmacValidator.validate` returns `true` because the signature only covers `B`.
5. `Registry.process` calls the registered handler with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)`, causing the host app to perform the webhook's action (e.g., record update, redaction, notification) as if it originated from `victim.myshopify.com`, despite the request never having been authenticated for that shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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
