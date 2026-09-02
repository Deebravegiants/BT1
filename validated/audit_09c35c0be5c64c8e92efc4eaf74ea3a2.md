Based on the investigation, I found a genuine identity-binding gap in this gem's webhook verification path.

### Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) header values are trusted without being covered by the HMAC, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` claims to "verify the request did indeed come from Shopify" before invoking the app's handler, but the HMAC it checks only signs the raw request body. The `shop` (and `topic`, `webhook_id`, `api_version`) values that are handed to the handler are read directly from unauthenticated HTTP headers, so they are not bound to the signature that was actually validated.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`ShopifyAPI::Utils::HmacValidator.validate` computes and compares the signature exclusively over that signable string: [2](#0-1) 

Meanwhile, `shop`, `topic`, `webhook_id`, and `api_version` are pulled straight from request headers, with no cryptographic tie to the body that was actually HMAC-verified: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately constructs `WebhookMetadata` from these unauthenticated header fields, handing them to the app's registered handler as if they had been verified as coming from Shopify for that shop/topic: [4](#0-3) 

The identity binding that is broken is: **`shop` claimed in the header != `shop` that produced the HMAC-signed body**. Since Shopify signs webhook payloads with the app's single shared `api_secret_key` across *all* shops that install the app (not a per-shop secret), any unprivileged user can install the target app on their own (attacker-controlled) shop, capture one legitimate webhook `(raw_body, hmac)` pair for their own shop, then replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary victim shop domain in the `x-shopify-shop-domain` header (and/or a different `topic`/`webhook-id`). `HmacValidator.validate` still returns `true` because it only checks the body, and `Registry.process` will happily call the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`.

### Impact Explanation
Any app that uses `data.shop` from a processed webhook to look up/act on a merchant's stored session, access token, or data (which is exactly the documented usage pattern shown in `docs/usage/webhooks.md` and expected by `WebhookMetadata`) can be tricked into processing attacker-supplied data or triggering shop-scoped side effects (e.g. cache invalidation, uninstall/GDPR-style flows, order/product sync) under an arbitrary victim shop identity. This is a cross-tenant identity confusion rooted entirely in this gem's own "verification" logic, not in host-app misuse, because the gem explicitly advertises that `process` "will verify the request did indeed come from Shopify."

### Likelihood Explanation
The only prerequisite is being able to install the target app once on any shop (freely obtainable via a Shopify dev/trial store) and reissue a captured HTTP request with one header changed — no access token, `client_secret`, or privileged account is required. This is trivially reachable by any unprivileged internet user who can reach the app's public webhook endpoint.

### Recommendation
Include the identity-relevant headers (`shop`, `topic`, `webhook_id`, `api_version`) in the HMAC-signed payload used by `to_signable_string`, or otherwise cryptographically bind them (e.g., derive/validate `shop` against a Shopify-issued signed value) before constructing `WebhookMetadata`, so header spoofing cannot decouple the verified body from the claimed tenant/topic.

### Proof of Concept
1. Install the target Shopify app on attacker-owned shop `attacker.myshopify.com`; trigger any webhook (e.g. `orders/create`) to capture a valid `(raw_body, x-shopify-hmac-sha256)` pair signed with the app's shared `api_secret_key`.
2. Replay the exact same `raw_body` and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but set `x-shopify-shop-domain: victim-shop.myshopify.com` (and optionally change `x-shopify-topic`/`x-shopify-webhook-id`).
3. `ShopifyAPI::Utils::HmacValidator.validate` succeeds because it only checks `raw_body` against the HMAC (`lib/shopify_api/utils/hmac_validator.rb:12-31`, `lib/shopify_api/webhooks/request.rb:35-38`).
4. `ShopifyAPI::Webhooks::Registry.process` invokes the app's handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", ...)` (`lib/shopify_api/webhooks/registry.rb:188-200`), causing the app to act as if Shopify verified a webhook for the victim shop.

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
