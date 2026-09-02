### Title
Webhook shop identity is not covered by the HMAC signature, allowing cross-tenant shop spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes/validates the webhook HMAC over the raw request body only, while the `shop` (tenant identity) is read from an unsigned HTTP header. An attacker who can obtain any one genuinely-signed webhook body/HMAC pair (e.g. by triggering a webhook on a shop they control) can replay it with an arbitrary `X-Shopify-Shop-Domain` / `shopify-shop-domain` header, and the signature will still validate — because that header is never part of the signed material. This breaks the identity binding `HMAC-verified-body == data-attributed-to(shop)`.

### Finding Description
`Request#to_signable_string` returns only the raw body: [1](#0-0) 

`Request#shop` is derived purely from a header, independent from the signed content: [2](#0-1) 

`Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)`, which calls `verifiable_query.to_signable_string` (body only) and `verifiable_query.hmac` — it never touches `shop`. After the HMAC check passes, `request.shop` is trusted and forwarded verbatim into the handler's `WebhookMetadata`: [3](#0-2) 

`Utils::HmacValidator.validate` only ever signs/verifies `verifiable_query.to_signable_string`, so any field excluded from that string (here, `shop`) is effectively unauthenticated: [4](#0-3) 

Compare this to the OAuth callback path, where `shop` IS included in the HMAC-signed string via `AuthQuery#to_signable_string`: [5](#0-4) 

So in the OAuth flow the binding `hmac-verified ⇒ shop-authentic` holds, but in the webhook flow it does not — the shop identity delivered to the handler (`WebhookMetadata#shop`, used by consuming apps to scope tenant data/session lookups) is entirely attacker-controllable as long as *some* valid `(body, hmac)` pair is presented.

### Impact Explanation
An attacker with a Shopify store of their own can legitimately receive real webhook deliveries (valid body + valid HMAC for their own shop's secret-derived signature, since Shopify signs webhooks with the app's `client_secret`, which is shared across all shops that installed the app — the HMAC secret is the same per-app, not per-shop). They can capture one such valid `(raw_body, hmac)` pair, then resend the request to the app's webhook endpoint with the `shop-domain` header changed to a victim/target shop. `HmacValidator.validate` will still pass because it verifies only the body against the shared app secret. The webhook handler will then process attacker-controlled data while believing it originated from the victim shop (`WebhookMetadata#shop`), which host applications commonly use to look up the shop's session/access token and to scope database writes — an identity/tenant binding break that can lead to cross-tenant data corruption or actions being taken under the wrong shop's session/context.

### Likelihood Explanation
Any developer/merchant installing the app can trivially generate a legitimate webhook for their own store, capture the raw body and `hmac-sha256` value, and replay it against the same endpoint with a forged shop-domain header — no secrets need to be guessed since the HMAC secret is the app's shared `client_secret`, already known to be valid for that same signature. This requires no elevated access beyond installing the app once.

### Recommendation
Include the shop identity (or another tenant-binding value delivered by Shopify) as part of the HMAC-signed material for webhooks, or otherwise cryptographically bind `shop-domain` to the signed body before trusting it in `WebhookMetadata`. At minimum, document/require that consuming applications cross-check `data.shop` against an independently-verified installed-shop list before using it to scope any data access or session lookup.

### Proof of Concept
1. Install the vulnerable app on `attacker-shop.myshopify.com`.
2. Trigger any subscribed webhook event (e.g., `orders/create`) on that shop; capture the raw POST body and the `X-Shopify-Hmac-Sha256` header Shopify sends.
3. Replay the exact same body + HMAC header to the app's webhook endpoint, but replace `X-Shopify-Shop-Domain` with `victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(...)` builds successfully; `Utils::HmacValidator.validate(request)` returns `true` because it only checks `raw_body` against the app secret (`lib/shopify_api/utils/hmac_validator.rb` and `lib/shopify_api/webhooks/request.rb#to_signable_string`).
5. `Registry.process` invokes the registered handler with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", body: <attacker-controlled JSON>)`, so any downstream logic keyed on `data.shop` operates on the victim tenant using attacker-supplied data.

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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
