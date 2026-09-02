Based on my analysis, I've confirmed the vulnerability pattern.

### Title
Webhook `shop-domain` header is not covered by HMAC verification, allowing cross-tenant shop spoofing - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, then trusts the `shop` value taken from the unauthenticated `X-Shopify-Shop-Domain` header when dispatching to the handler. The `shop` field is never part of the signed material, so the equality the code implicitly relies on — "shop that produced this signed payload" == "shop the handler is told the payload belongs to" — does not actually hold.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) , and the `hmac` used for verification is likewise derived only from the `hmac-sha256` header value, not from any other header: [2](#0-1) . The `shop` accessor simply reads the `shopify-shop-domain`/`x-shopify-shop-domain` header verbatim, with no cross-check against the signed content and no `ShopValidator` sanitization: [3](#0-2) .

`Registry.process` validates the HMAC of the request (i.e., proves the body bytes were signed by `Context.api_secret_key`) and then immediately forwards the unauthenticated `request.shop` to the app's handler: [4](#0-3) . The `HmacValidator.validate` call only checks `verifiable_query.to_signable_string` (the raw body) against the HMAC: [5](#0-4) .

Because the byte range that is *verified* (raw body only) is narrower than the byte range that is *parsed and acted upon* (raw body + `shop-domain` header), an attacker who can obtain one genuinely-signed webhook body (trivially available to any merchant/developer who installs the app on their own store and receives a real webhook) can replay that body to the app's public webhook endpoint while substituting an arbitrary victim shop domain in the `X-Shopify-Shop-Domain` header. The HMAC still validates (it only covers the body), and `WebhookMetadata.new(shop: request.shop, ...)` passes the attacker-chosen shop identity straight to the handler: [6](#0-5) .

### Impact Explanation
This breaks the tenant-identity binding the whole webhook-authentication scheme is meant to provide: "authenticated sender" vs. "shop attributed to the event." Host applications commonly use `data.shop` from `WebhookMetadata` to look up the merchant's stored session/access token and perform actions or store attacker-controlled payload data under that shop's record — this is the documented and expected usage of the webhook handler interface. An attacker controlling their own shop's webhook body can therefore inject data attributed to a different tenant (cross-tenant data confusion) purely by manipulating an unauthenticated header, without ever needing the app's `client_secret`, an access token, or any privileged credential.

### Likelihood Explanation
Exploitability depends on the webhook endpoint being reachable with attacker-controlled headers (true for most publicly deployed webhook receivers, since Shopify webhook delivery is by design a public HTTPS callback and the gem does not restrict by source IP), and on the attacker being able to produce at least one genuinely-signed payload (trivial: install the app to any store you control, or use any topic that fires on a low-privilege action in your own shop). No secret material is required from the app.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the signed material verified against the HMAC, or otherwise cryptographically bind the `shop` value to the payload before trusting it — e.g., require host applications to cross-check `request.shop` against the shop associated with the session/webhook-id looked up via a trusted, authenticated channel (GraphQL query by `webhook_id`) rather than trusting the header value directly for identity-sensitive decisions. At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated and must not be used as a tenant identifier without additional verification.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a webhook (e.g. `orders/create`) with an attacker-controlled body, obtaining a valid `X-Shopify-Hmac-Sha256` value for that raw body.
2. Attacker (or a network intermediary capable of reaching the app's public webhook URL) sends this exact raw body and HMAC header to the app's webhook endpoint, but replaces `X-Shopify-Shop-Domain: attacker-shop.myshopify.com` with `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks the raw body against the HMAC (`lib/shopify_api/utils/hmac_validator.rb:26-31`, `lib/shopify_api/webhooks/request.rb:35-38`).
4. `handler.handle(data: WebhookMetadata.new(..., shop: request.shop, ...))` is invoked with `shop == "victim-shop.myshopify.com"` even though the payload actually originated from the attacker's own shop (`lib/shopify_api/webhooks/registry.rb:188-199`, `lib/shopify_api/webhooks/request.rb:20-23`).

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
