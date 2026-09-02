This confirms the analog: the `ShopifyAPI::Webhooks::Request#to_signable_string` method returns only `@raw_body`, meaning the HMAC signature computed by `Utils::HmacValidator.validate(request)` covers solely the request body and never the `shopify-topic`, `shopify-shop-domain`, `shopify-webhook-id`, or `shopify-api-version` headers. [1](#0-0) 

`Registry.process` verifies only that HMAC, then trusts `request.shop`, `request.topic`, and `request.webhook_id` — all pulled straight from unauthenticated headers — to build `WebhookMetadata` passed to the app's handler. [2](#0-1) 

The shared secret (`api_secret_key`) used for HMAC validation is scoped to the **app**, not to an individual shop [3](#0-2) , so any shop that installs the app receives Shopify-originated webhooks whose HMAC is computed with that same secret.

### Title
Webhook `shop-domain` (and `topic`/`webhook-id`) header is not covered by the HMAC, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw body, so `Utils::HmacValidator.validate` in `Registry.process` verifies the payload bytes but never binds the `shopify-shop-domain`, `shopify-topic`, or `shopify-webhook-id` headers to that signature. Any party that can produce a body+HMAC pair valid for the shared app secret (e.g., a shop that has installed the app and receives its own legitimate webhooks) can replay that exact body+HMAC while substituting arbitrary header values for shop, topic, and webhook id, and the library will accept it as authentic.

### Finding Description
`Request#hmac` decodes the `hmac-sha256` header and `to_signable_string` returns `@raw_body` — nothing else [4](#0-3) . `HmacValidator.validate` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it to the supplied `hmac` [5](#0-4) . Since only the body is signed, the equality actually verified is:

`HMAC(api_secret_key, raw_body) == received_hmac`

but the code then trusts a *different, unverified* binding downstream:

`request.shop == "the shop this webhook is about"`

These two are not the same claim. `Registry.process` raises only if the body-HMAC check fails, then immediately uses `request.shop`, `request.topic`, and `request.webhook_id` — read directly from headers with no cryptographic tie to the signed body — to build `WebhookMetadata` and dispatch it to the app's handler [6](#0-5) . Because `api_secret_key` is a single per-app secret shared across every shop that installs the app [7](#0-6) , a malicious shop owner who has installed the app receives Shopify-signed webhooks for their own shop's topics/bodies, then can send the identical raw body and HMAC to the app's webhook endpoint while swapping the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) header to name a victim shop. The gem's `process` method has no way to detect this substitution because the header was never part of the signed material.

### Impact Explanation
This breaks the tenant-isolation guarantee that webhook handlers rely on: a handler that trusts `WebhookMetadata#shop` to scope data lookups, cache keys, or authorization decisions can be made to act on/for a shop it did not actually receive a notification about. This is a cross-tenant confusion primitive reachable by any shop that has installed the app (an unprivileged, non-victim tenant), requiring no access to the app's `client_secret` or any victim credentials — only a legitimate webhook received for the attacker's own store.

### Likelihood Explanation
Any merchant/developer who installs the app can trivially capture a real webhook (raw body + valid HMAC header) sent to their own endpoint, then replay it with a modified shop-domain header to the same endpoint. No secret material needs to be reverse engineered; the attacker only needs a webhook that was legitimately sent for their own shop.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the signed material that `to_signable_string` returns, or otherwise cryptographically bind the header values used downstream (e.g., cross-check `request.shop` against session/shop metadata associated with the registration) before dispatching to `handler.handle`. At minimum, document that `Registry.process` does not authenticate the shop/topic/webhook-id headers and require host applications to independently verify shop ownership.

### Proof of Concept
1. App installs webhook handler for topic `orders/create` for both `shop-a.myshopify.com` and `shop-b.myshopify.com` (both installed the same app, sharing one `api_secret_key`).
2. Shopify sends a legitimate webhook to the app for `shop-a.myshopify.com`:
   ```
   POST /webhooks
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: <valid HMAC of body, computed with api_secret_key>
   X-Shopify-Shop-Domain: shop-a.myshopify.com
   Body: {"id": 123, ...}
   ```
3. The attacker (owner/operator of `shop-a`) intercepts and resends the exact same body and `X-Shopify-Hmac-Sha256` value, but changes the header:
   ```
   X-Shopify-Shop-Domain: shop-b.myshopify.com
   ```
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(api_secret_key, raw_body)` — unchanged, since the body is identical — and it matches, so validation passes [8](#0-7) .
5. `handler.handle` is invoked with `WebhookMetadata.new(shop: "shop-b.myshopify.com", ...)`, so the app processes attacker-controlled/shop-a's order data as if it belonged to `shop-b`, or otherwise triggers shop-b-scoped side effects using shop-a's data — a cross-tenant data/identity confusion.

### Citations

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
