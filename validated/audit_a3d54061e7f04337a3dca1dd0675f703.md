### Title
Webhook HMAC signs only the raw body, not the shop identity, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` exposes `shop` (the merchant identity used by webhook handlers) as an untrusted HTTP header, while `to_signable_string` — the value that `Utils::HmacValidator` actually authenticates — only covers the raw request body. The HMAC therefore proves "this body was produced with the app's secret," but never proves "this body belongs to this shop." Any party who can obtain one genuine, validly-signed webhook body (e.g., by installing the app on their own store) can replay that same body/HMAC pair to the app's webhook endpoint while substituting the `shopify-shop-domain` (or `x-shopify-shop-domain`) header for a victim shop, and `Registry.process` will accept it as authentic for the victim shop.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read directly from an attacker-controllable header with no cryptographic binding to the body or the HMAC: [2](#0-1) 

`Registry.process` validates only the HMAC-over-body via `Utils::HmacValidator.validate(request)`, then immediately trusts `request.shop` as the tenant identity forwarded to the app's handler: [3](#0-2) 

`HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string` (the body) and the shared `Context.api_secret_key`: [4](#0-3) 

This is the exact bug class described in the analog report: a field that is *acted on* (`shop`, used as the tenant/session key passed to `WebhookMetadata`) is not covered by the authenticity check (the HMAC), breaking the equality that should hold: `shop_bound_by_hmac == shop_used_by_handler`. Because a single `client_secret` is shared across every shop that installs the app, any merchant (an unprivileged party relative to other tenants) who receives one legitimate webhook for their own store can capture that body+HMAC pair and resend it to the app's webhook endpoint with a different `shop-domain` header, passing validation while impersonating another shop.

### Impact Explanation
This breaks cross-tenant isolation: the webhook handler receives `WebhookMetadata#shop` (and possibly the corresponding parsed body) attributed to a shop that never actually sent the data. Depending on how the host application uses `data.shop` (e.g., to look up which merchant's session/access token to act with, to trigger data sync, or to gate business logic), an attacker can inject spoofed data attributed to a victim shop, or trigger side effects scoped to a shop they don't own — a cross-tenant access/confusion vulnerability, which meets the Critical bar (cross-tenant access) defined in scope.

### Likelihood Explanation
Any user can independently install the target app on their own trial/dev store, which is unprivileged and requires no special access to the target app's `client_secret`, access tokens, or the victim's credentials. Once they have one legitimately signed webhook (trivial to obtain since it's delivered automatically after registering any webhook topic), replaying it with a modified shop header is a simple HTTP request. No cryptographic secret needs to be broken.

### Recommendation
Bind the shop identity into the signed payload verification path, e.g., include `shop` (and ideally `topic`/`webhook_id`) in `to_signable_string`'s comparison — but since Shopify's real webhook HMAC scheme signs only the body, mitigation should instead be to explicitly validate `request.shop` against an expected/registered shop context (per-shop secret or explicit shop allow-list) before handing `WebhookMetadata` to handlers, and to document prominently that `request.shop` is header-derived and NOT covered by the HMAC signature, so host applications don't treat it as an authenticated tenant identifier without additional verification.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and registers a webhook topic (e.g. `orders/create`).
2. Shopify delivers a legitimately signed webhook: body `B`, header `x-shopify-hmac-sha256: H` (valid for secret `S`), `x-shopify-shop-domain: attacker.myshopify.com`.
3. Attacker resends the identical body `B` and `x-shopify-hmac-sha256: H` to the app's webhook endpoint, but replaces the header with `x-shopify-shop-domain: victim.myshopify.com`.
4. `Utils::HmacValidator.validate(request)` recomputes HMAC over `B` only and it matches `H`, so `Registry.process` proceeds: [5](#0-4) 
5. The handler executes `handle(data: WebhookMetadata.new(..., shop: "victim.myshopify.com", body: parsed(B), ...))`, processing attacker-controlled data as if it originated from `victim.myshopify.com`.

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
