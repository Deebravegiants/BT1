The gem's own documentation states that `ShopifyAPI::Webhooks::Registry.process` "will verify the request did indeed come from Shopify" (`docs/usage/webhooks.md:125`), and it exposes `data.shop` in `WebhookMetadata` as "The shop domain of the webhook" (`docs/usage/webhooks.md:14`) — i.e., the gem's documented contract promises that after `process` succeeds, `shop` is an authenticated, trustworthy identifier of the tenant. That promise is violated by the implementation.

### Title
Webhook tenant identity spoofing via unauthenticated `shop-domain` header — HMAC signs only the body, not the shop/topic/webhook-id headers ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by checking that `HMAC-SHA256(secret, raw_body)` matches the `hmac-sha256` header, then trusts the `shop-domain`, `topic`, and `webhook-id` headers verbatim when building `WebhookMetadata` for the handler.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`ShopifyAPI::Utils::HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` (the body only) and compares it to the `hmac` header: [2](#0-1) 

`Registry.process` gates on this HMAC check, then immediately builds `WebhookMetadata` using `request.shop`, `request.topic`, and `request.webhook_id`, none of which are covered by the signature: [3](#0-2) 

`shop`, `topic`, and `webhook_id` are all read directly from HTTP headers with no cryptographic tie to the body/signature: [4](#0-3) 

The identity binding that should hold is: `shop header == shop authenticated by the signature`. Instead, the signature only proves `body == body signed by holder of api_secret_key`; it says nothing about which shop or topic that body belongs to. Since `api_secret_key` is the app's single `client_secret` shared across every shop that installs the app (not a per-shop secret), any merchant who installs the app — including an attacker who installs it on their own store, i.e., an unprivileged internet user — legitimately receives real `(raw_body, hmac)` pairs signed with that same secret. The attacker can then replay that exact body to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`, `X-Shopify-Webhook-Id`) header for a victim shop. `HmacValidator.validate` still passes because the body is unmodified and the secret is identical for all tenants, and `Registry.process` will invoke the app's handler with `data.shop` set to the victim shop, `data.topic` set to whatever topic the attacker chooses, and `data.body` set to the attacker-controlled (but validly-signed-for-a-different-shop) content.

### Impact Explanation
This breaks the cross-tenant boundary the gem is documented to enforce ("This will verify the request did indeed come from Shopify"): a webhook signature that is only proof of "signed by this app's secret" is presented to consumers as proof of "this exact event happened for this exact shop." Any downstream logic that keys off `data.shop` to attribute writes, side effects, billing, or state transitions to a merchant record can be tricked into applying attacker-supplied data to an arbitrary victim shop, which is a cross-tenant access/data-integrity violation requiring no privileged credentials — only a self-service app installation available to any internet user.

### Likelihood Explanation
Any user can install an app that uses this gem on their own free/development Shopify store, trigger any subscribed webhook topic (e.g., `orders/create`) to obtain a real `(raw_body, hmac)` pair signed with the app's shared `client_secret`, and then POST that same body with a forged `shop-domain` header to the app's public webhook endpoint. No secrets, tokens, or elevated access are needed beyond what a normal merchant installation grants.

### Recommendation
Include the security-relevant headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the signable string used for HMAC verification, or otherwise cryptographically bind them to the body before trusting them in `WebhookMetadata`, so that `HmacValidator.validate` authenticates the full identity tuple `(shop, topic, webhook_id, body)` and not just the raw body bytes.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and triggers `orders/create`, capturing the raw POST: headers include `X-Shopify-Hmac-Sha256: <valid>`, `X-Shopify-Shop-Domain: attacker.myshopify.com`, `X-Shopify-Topic: orders/create`, and body `B`.
2. Attacker replays the exact same request to the app's webhook endpoint, changing only `X-Shopify-Shop-Domain` to `victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)` is constructed; `Utils::HmacValidator.validate` recomputes `HMAC(secret, B)`, which still matches the unmodified body's HMAC.
4. `Registry.process` calls the app's handler with `WebhookMetadata.new(topic: "orders/create", shop: "victim.myshopify.com", body: parsed(B), ...)`, causing the app to process attacker-controlled webhook content as if it originated from the victim shop.

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
