## Title
Webhook `shop-domain` (and `topic`/`api_version`/`webhook_id`) headers are not covered by the HMAC signature, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC of the raw request body. The shop identity that the app actually acts on (`shop-domain` header) is read from an unauthenticated HTTP header and is never included in the signed payload, breaking the equality `shop_authenticated == shop_acted_upon`.

### Finding Description
`ShopifyAPI::Utils::HmacValidator.validate` verifies a webhook by recomputing the HMAC over `verifiable_query.to_signable_string` and comparing it to the received signature: [1](#0-0) 

For `ShopifyAPI::Webhooks::Request`, `to_signable_string` returns only the raw HTTP body (`@raw_body`) — it does **not** include the `shop`, `topic`, `webhook_id`, or `api_version` values, which are instead read directly from unauthenticated HTTP headers: [2](#0-1) 

`Registry.process` validates the HMAC and then immediately dispatches to the app's handler using `request.shop` — the unauthenticated header value — as the tenant identity: [3](#0-2) 

Because Shopify's webhook HMAC secret is the app's single shared `api_secret_key` (identical for every shop that has the app installed) and the signature only binds the body bytes — not the shop — any actor who can obtain one legitimately-signed `(body, hmac)` pair (e.g., by installing the app on their own store, a `myshopify.io`/`shopify.com` free/trial shop anyone can create, and receiving a real webhook for an event they trigger) can replay that exact body to the app's webhook endpoint while substituting an arbitrary `shop-domain` header value. `HmacValidator.validate` will still pass because it only checks the body's signature, and `Registry.process` will hand the payload to the app's business logic tagged with the attacker-chosen shop. This is exactly the "field acted on but not covered by the HMAC" identity-binding break called out in the rules: the equality `shop_bound_by_signature (none) == shop_used_for_dispatch (request.shop)` does not hold.

### Impact Explanation
This allows a low-privilege actor (any merchant/developer who can install the app on a store they control) to forge webhook events that the app will process as belonging to a *different* tenant's shop, since the shop identifier is never cryptographically bound to the signed content. Depending on how the host application's webhook handler uses `WebhookMetadata#shop` (e.g., updating billing state, order/customer records, uninstall/GDPR handling, or app-managed entitlements keyed by shop), this is a cross-tenant data integrity/confusion vector — matching the Critical "cross-tenant access" impact category, since it lets one tenant inject events attributed to another tenant purely through header manipulation, bypassing the shop-identity guarantee the HMAC check is meant to provide.

### Likelihood Explanation
Likelihood is moderate-to-high in practice: obtaining one valid `(body, hmac)` pair is trivial for anyone who installs the app on their own store (a free action) and simply lets Shopify send them a real webhook (e.g., `app/uninstalled`, `orders/create` on a test order); the attacker then only needs to change the `shop-domain` (and optionally `topic`/`webhook_id`) header and POST it directly to the app's public webhook endpoint — no cryptographic material is required, and the request will pass the `Utils::HmacValidator.validate` check unchanged since the signature never covered those headers.

### Recommendation
Bind the shop (and ideally topic/webhook id) into the value that is HMAC-verified, or otherwise cross-check header-derived identity against a value the app independently trusts (e.g., verifying `shop` against the shop associated with the specific webhook `id`/subscription previously registered, or requiring the caller to confirm the shop is one this app instance has an active session/access token for) before dispatching to handlers. At minimum, document that `WebhookMetadata#shop` is unauthenticated and must not be trusted for authorization decisions without additional verification by the host application.

### Proof of Concept
1. Install the target app on an attacker-controlled Shopify dev/trial store (`attacker-shop.myshopify.com`) and capture one real webhook delivery, e.g.:
   - Headers: `x-shopify-hmac-sha256: <validHmac>`, `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: orders/create`
   - Body: `{"id":123, ...}`
2. Replay the exact same body and `x-shopify-hmac-sha256` value to the app's public webhook endpoint, but change the header:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
3. `ShopifyAPI::Utils::HmacValidator.validate` recomputes the HMAC over the (unchanged) body only — using `lib/shopify_api/utils/hmac_validator.rb` `validate_signature` — and it matches, so `Registry.process` (`lib/shopify_api/webhooks/registry.rb` line 190) proceeds and calls the app's handler with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)`, even though the payload never actually came from Shopify on behalf of `victim-shop.myshopify.com`.

### Citations

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
