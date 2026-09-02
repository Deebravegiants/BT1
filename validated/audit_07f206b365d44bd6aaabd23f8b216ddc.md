### Title
Webhook shop identity (`shopify-shop-domain`) is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) that is handed to the app's `WebhookHandler` from the unauthenticated `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header, while the HMAC signature that `Utils::HmacValidator.validate` checks only covers the raw request body, never the shop-domain header. This breaks the binding: `HMAC-verified bytes == the identity the app acts on`.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read straight from the `shopify-shop-domain` header with no cross-check against the signed content: [2](#0-1) 

`Registry.process` validates the HMAC over the `Request` object, then immediately trusts `request.shop` to build `WebhookMetadata` that is dispatched to the app's handler: [3](#0-2) [4](#0-3) 

`HmacValidator.validate` only checks `verifiable_query.hmac` against `compute_signature(verifiable_query.to_signable_string, secret)` — i.e., the raw body — using the app's single shared `api_secret_key` (the same secret is valid for webhooks from every shop that has installed the app, since Shopify signs webhooks with the app's client secret, not a per-shop key): [5](#0-4) 

**Binding that should hold:** `shop header used by WebhookHandler == shop whose bytes were HMAC-verified`.
**What actually holds:** `HMAC(raw_body, shared_api_secret_key) == valid` regardless of which shop's header accompanies it, because the shop-domain header is entirely outside `to_signable_string`.

Because the app's secret is shared across all shops that install the app, any party who can obtain one validly-signed webhook payload+HMAC pair (e.g., by legitimately installing the app on their own shop and receiving a real webhook, or observing one in transit) can replay the identical `raw_body`/`hmac-sha256` pair to the app's webhook endpoint while substituting the `shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` will still pass (it never looks at the header), and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload came from the victim shop.

### Impact Explanation
This is a cross-tenant identity-spoofing primitive: the gem allows an attacker-controlled shop to have their own webhook traffic accepted by the app while impersonating a different, victim shop. Any app logic that keys state, deduplication, GDPR redaction, order/customer sync, or session lookups off `WebhookMetadata#shop` can be manipulated into acting on the wrong tenant's data path, since the framework provides no verified linkage between the cryptographically-checked bytes and the shop identity attached to them. This matches the "Critical - cross-tenant access" impact category, since the vulnerable binding is enforced entirely inside this gem's `Webhooks::Request`/`Registry`/`HmacValidator` code, not by any host-application choice.

### Likelihood Explanation
Exploitation requires only the ability to install the app on an attacker-controlled development/trial shop (an ordinary, unprivileged action any internet user can take for a public app) to obtain one legitimately-signed webhook body/HMAC pair, then replay it with a forged `shopify-shop-domain` header to the app's public callback endpoint. No access token, `api_secret_key`, or privileged credential is needed — the whole point of the flaw is that the shared secret's validity is independent of the shop header.

### Recommendation
Bind the shop identity to the HMAC-verified payload:
- Include the shop domain (and topic) inside `to_signable_string`, or
- Require the app to independently verify that `request.shop` corresponds to an install for which the app expects this specific webhook (e.g., look up an existing session/shop record before trusting `WebhookMetadata#shop`), or
- At minimum, document explicitly that `shop` in `WebhookMetadata` is not HMAC-covered and must not be trusted as an authenticated identity without further server-side verification against known installed shops.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and lets the app register a real webhook (e.g., `orders/create`).
2. Shopify sends a legitimate webhook with `raw_body = B` and header `x-shopify-hmac-sha256 = HMAC(B, app_secret)` (the same `app_secret` is used for every shop installing this app).
3. Attacker captures `(B, HMAC(B, app_secret))` and replays it to the app's webhook endpoint, but changes the header `x-shopify-shop-domain` to `victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request#hmac` re-derives the same HMAC value from the header; `HmacValidator.validate` recomputes `HMAC(B, app_secret)` (via `to_signable_string` = `B`) and it matches, since the shop header plays no role in the signature: [6](#0-5) 
5. `Registry.process` calls the app's handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed B, ...)`, causing the app to act as if the attacker-controlled payload originated from the victim shop. [3](#0-2)

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
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
