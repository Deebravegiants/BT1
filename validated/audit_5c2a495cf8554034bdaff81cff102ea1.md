### Title
Webhook `shop` (and `topic`) identity is trusted from an unauthenticated header while the HMAC only covers the raw body, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies a webhook by validating an HMAC that is computed **only** over the raw request body, then passes the `shop` (and `topic`) values taken from HTTP headers — which are never part of the signed data — straight to the merchant's handler code. Any party capable of producing one valid, HMAC-signed webhook payload (e.g. the owner/admin of any shop that has installed the app) can replay that exact body with the `shop-domain`/`x-shopify-shop-domain` header rewritten to a different shop, and the gem will report it as a verified webhook for the victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body: [1](#0-0) 

`shop` and `topic`, however, are read straight from attacker-controlled HTTP headers and are not part of the signed material: [2](#0-1) 

`Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)` — which internally calls `request.to_signable_string` (the raw body) against `request.hmac` — and then, once that check passes, forwards `request.shop` and `request.topic` unchecked to the registered handler: [3](#0-2) 

The HMAC validator itself only ever signs/verifies `verifiable_query.to_signable_string`, i.e. whatever the object under test chooses to include: [4](#0-3) 

This breaks the intended identity binding: `hmac == HMAC(body)` is treated by the gem as if it also proved `shop == <claimed shop>`, but that equality is never checked. Since the app's `api_secret_key` is shared across every shop that has installed the app (it is a per-app secret, not per-shop), any shop that has installed the app can generate a real, validly-signed webhook for itself (e.g. by triggering `orders/create` in its own store), capture the body + `x-shopify-hmac-sha256` value, and then POST that identical body/signature pair to the app's webhook endpoint with `x-shopify-shop-domain` changed to point at a victim shop. `Registry.process` will accept it as authentic and dispatch `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: ..., body: ...)` to the app's handler.

### Impact Explanation
This is a cross-tenant integrity issue: a shop that is merely one of many app installs (an "unprivileged" tenant relative to other merchants) can forge webhook events that the app attributes to a different merchant's shop. Depending on what the app does with webhooks (e.g. `app/uninstalled` cleanup, `shop/redact` or `customers/redact` GDPR handlers, billing/subscription state changes, order processing), this can be used to trigger data deletion, session/token revocation, or state changes for a shop the attacker does not own and has no access to — a cross-tenant access/integrity violation carried out purely through this gem's webhook-verification contract.

### Likelihood Explanation
Any merchant who installs the app already has everything needed: they can trigger legitimate webhook events for their own shop, capture the raw body and its valid `hmac-sha256` header (both delivered to their own accessible endpoint/logs), and replay them with a modified `shop-domain` header to the app's public webhook endpoint. No access to `api_secret_key`, access tokens, or any other shop's credentials is required — only participation as an ordinary installed tenant.

### Recommendation
Bind the shop (and topic) identity into the verified material instead of trusting bare headers:
- Include `shop` (and ideally `topic`, `webhook_id`, and a timestamp/nonce) in the string that is HMAC-verified, or
- Require the caller (host application) to separately confirm that `request.shop` matches a shop with a currently valid, stored access token/session before dispatching, and have `Registry.process` enforce/document this as a mandatory step rather than leaving it implicit, or
- At minimum, document loudly in `ShopifyAPI::Webhooks::Registry.process` and `Request` that `shop`/`topic` are unauthenticated header values and must be independently validated by the host app against known installed shops before being trusted for any privileged action.

### Proof of Concept
1. App is installed on `attacker-shop.myshopify.com` and on victim `victim-shop.myshopify.com`, both under the same Shopify app (shared `api_secret_key`).
2. Attacker triggers a real webhook (e.g. updates a product) on their own shop, capturing:
   - raw body `B`
   - header `x-shopify-hmac-sha256: H` (valid HMAC of `B` under the shared `api_secret_key`)
3. Attacker sends a POST to the app's webhook endpoint with:
   - body `B` (unchanged)
   - `x-shopify-hmac-sha256: H` (unchanged, still valid because HMAC is over body only)
   - `x-shopify-shop-domain: victim-shop.myshopify.com` (rewritten)
   - `x-shopify-topic` set to whatever topic/handler the attacker wants to invoke
4. `Registry.process` calls `Utils::HmacValidator.validate(request)` which succeeds (body/HMAC still match), then dispatches `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: ..., body: parsed(B), ...)` to the handler, which the app treats as an authentic event for `victim-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
