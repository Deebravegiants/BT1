## Title
Cross-Tenant Webhook Spoofing via Unsigned `shop-domain` Header - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC computed over the raw request body, but the `shop` (and `topic`/`webhook_id`) values that the library hands to the app's handler as the tenant identifier come from unsigned HTTP headers. Because a single app's `api_secret_key` is shared across every merchant who installs that app, a malicious merchant can capture a genuine, validly-signed webhook delivered to their own shop and replay the same body+HMAC to the app's webhook endpoint with a forged `X-Shopify-Shop-Domain` header pointing at a victim shop. The library will treat this as fully authenticated for the victim tenant.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is not part of the signed data: [2](#0-1) 

`HmacValidator.validate` and `validate_signature` only ever HMAC the `to_signable_string` value (the raw body) with `Context.api_secret_key`: [3](#0-2) 

`Registry.process` performs this HMAC check and, on success, immediately forwards the unsigned `request.shop` value to the app's handler as authoritative tenant context: [4](#0-3) 

The broken identity binding is:
`shop authenticated by HmacValidator.validate(request)` ≠ `shop actually bound to the signed bytes (@raw_body)`.

Since `Context.api_secret_key` is the app's single client secret used to sign webhooks for *every* shop that has the app installed (not a per-shop secret), any attacker who can install the app on their own store receives real webhooks signed with that same secret. They can then replay the identical `raw_body` + `hmac` pair to the app's webhook endpoint while substituting the `shop-domain` header for a victim shop's domain. `HmacValidator.validate` still succeeds (it never looks at the shop header), so `Registry.process` calls the handler with `WebhookMetadata.new(... shop: request.shop ...)` pointing at the victim, even though the payload content was never actually generated for, nor signed on behalf of, that shop.

### Impact Explanation
This crosses a tenant boundary: an app built on top of this library's `Webhooks::Registry` — which explicitly gates handler execution on `Utils::HmacValidator.validate(request)` as its authentication step — will treat the forged `shop` as trustworthy since it is only exposed after that validation gate. Depending on the webhook topic, an attacker-controlled payload can be attributed to a victim tenant, e.g. forging `app/uninstalled`, `customers/redact`, or order/customer webhooks that cause the app to mutate victim-shop data, delete victim sessions, or process attacker-supplied content as though it originated from the victim's store. This matches the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Exploitation requires only that the attacker be able to install the target app on a shop they control (a normal, unprivileged action for any Shopify merchant/developer) in order to obtain a validly-signed webhook body+HMAC pair, then send a crafted HTTP request to the app's public webhook endpoint with a different `shop-domain` header — no access token, `client_secret`, or privileged account needed.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook-id`) values into the data actually covered by the HMAC, or require callers of `Registry.process` to cross-check `request.shop` against an independently-verified/expected shop (e.g., the shop associated with the merchant record the webhook claims to be for) before trusting it. At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated and must not be used as a sole tenant-identity source.

### Proof of Concept
1. Attacker installs the target app on `attacker.myshopify.com`. Shopify sends a real webhook, e.g. `orders/create`, with body `B`, header `x-shopify-shop-domain: attacker.myshopify.com`, and `x-shopify-hmac-sha256: HMAC(secret, B)`.
2. Attacker captures `B` and the HMAC value.
3. Attacker POSTs the same `B` and HMAC to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)` — this passes because it only checks `B` against the HMAC using the shared `api_secret_key`.
5. The handler is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed(B), ...)`, causing the app to process attacker-controlled content as belonging to `victim.myshopify.com`.

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
