### Title
Webhook `shop-domain`, `topic`, and `webhook_id` headers are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC over the raw request body only, while the tenant-identifying `shop-domain` header (plus `topic`, `webhook_id`, `api_version`) is read directly from unauthenticated HTTP headers and passed straight through to the app's webhook handler. `Registry.process` verifies the HMAC but never binds it to these header values, so an attacker who can obtain any validly-HMAC-signed body (e.g., from webhooks Shopify sends for their own trial/dev shop) can replay it with a forged `shop-domain` header and have the app process it as if it belonged to a different merchant.

### Finding Description
The binding that should hold is:

`shop authenticated by HMAC == shop the app acts on`

In `lib/shopify_api/webhooks/request.rb`:
- `shop` is read from the `shopify-shop-domain`/`x-shopify-shop-domain` header: [1](#0-0) 
- `topic`, `api_version`, and `webhook_id` are likewise taken from headers: [2](#0-1) 
- But `to_signable_string`, which is what `HmacValidator` actually signs/verifies, is only the raw body — none of the headers are included: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately hands `request.shop`, `request.topic`, and `request.webhook_id` — all unauthenticated header values — to the registered handler: [4](#0-3) 

Since `HmacValidator.validate` only checks `hmac == HMAC(secret, raw_body)` [5](#0-4) , any HTTP request with a body/HMAC pair that was legitimately produced by Shopify for *some* shop will pass validation regardless of what `shop-domain` header accompanies it. The equality that should be enforced — "the shop credited with this HMAC-signed payload equals the shop the handler treats as the source of truth" — is never checked; only the body bytes are checked, not the header bytes that are actually consumed by the application.

### Impact Explanation
Handlers commonly key off `WebhookMetadata#shop` to decide which merchant's session/access token/data to look up, mutate, or delete (e.g., `app/uninstalled` to revoke a session, `shop/redact` or `customers/redact` to erase data, or business webhooks that update per-shop state). Because `shop` is not bound to the HMAC, an attacker who has access to any one legitimately-signed webhook body/HMAC pair (trivial to obtain by installing the app on a free/dev store they control and letting Shopify deliver a webhook) can resend that same body with the `shop-domain` header rewritten to a victim shop. The app will process it believing it originates from the victim tenant — a cross-tenant identity confusion that can lead to unauthorized data mutation/deletion or improper session/token revocation for a shop the attacker does not control.

### Likelihood Explanation
Exploitation requires only: (1) being able to trigger any real webhook delivery to the app (trivially done by installing the app on any shop, including a free development store, since webhook subscriptions and mandatory topics fire automatically), and (2) replaying that HTTP POST with a modified `X-Shopify-Shop-Domain` (and optionally `X-Shopify-Topic`) header to the app's public webhook endpoint. No access token, `api_secret_key`, or privileged account is needed — the attacker never needs to compute a valid HMAC themselves, only capture and replay one that Shopify already computed for a body they control.

### Recommendation
Include `shop-domain`, `topic`, `api_version`, and `webhook_id` in the HMAC-signable payload (or otherwise cryptographically bind them to the verified body), or validate the `shop-domain` header against an out-of-band trusted source (e.g., the currently installed session/shop for the endpoint) before dispatching to handlers, rather than trusting header values that sit outside the HMAC.

### Proof of Concept
1. Attacker installs the app on their own (e.g., free development) shop `attacker.myshopify.com` and lets Shopify deliver any subscribed webhook, e.g. `app/uninstalled`, capturing the raw POST body and its legitimate `X-Shopify-Hmac-Sha256` header.
2. Attacker resends this exact body/HMAC pair to the app's webhook endpoint, but replaces the `X-Shopify-Shop-Domain` header with `victim-shop.myshopify.com` (and, if desired, `X-Shopify-Topic`).
3. `Utils::HmacValidator.validate(request)` succeeds because it only checks the raw body against the HMAC [6](#0-5) .
4. `Registry.process` looks up the handler by `request.topic` and invokes it with `shop: request.shop` set to `victim-shop.myshopify.com` [7](#0-6) , causing the host application's handler (e.g., session/token revocation on `app/uninstalled`, or data erasure on `shop/redact`) to act against the victim shop's tenant data instead of the attacker's own.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
