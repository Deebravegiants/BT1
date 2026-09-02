## Finding

### Title
Webhook Shop Attribution Not Bound to HMAC Signature Allows Cross-Tenant Webhook Spoofing - (`lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw request body only, while the `shop` attribute used to attribute the webhook to a tenant is read from a separate, unsigned HTTP header. Because a single `api_secret_key` is shared by an app across every shop that installs it, any unprivileged party who installs the app on a shop they control can capture one legitimately-signed webhook delivery and replay its body/HMAC pair to the app's webhook endpoint while substituting an arbitrary victim `shop-domain` header. `Utils::HmacValidator` and `Webhooks::Registry.process` will accept the request as valid and dispatch it to the app's handler with the attacker-chosen shop, breaking the binding between "HMAC-authenticated bytes" and "shop attribution."

### Finding Description
`Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

and `shop` is derived independently from an unauthenticated header: [2](#0-1) 

`Utils::HmacValidator.validate` verifies only that the body's HMAC matches `Context.api_secret_key` (or `old_api_secret_key`); it never checks or binds the `shop` header: [3](#0-2) 

`Webhooks::Registry.process` then trusts `request.shop` as-is once the HMAC of the body passes, and forwards it to the app's handler as the tenant identifier: [4](#0-3) 

Because `Context.api_secret_key` (the app's `client_secret`) is the same value for every shop that installs the app, any unprivileged actor can:
1. Install the target app on a shop they control (free dev store or trial install — no privileged credential needed).
2. Capture one authentic webhook delivery from Shopify (raw body + `X-Shopify-Hmac-SHA256` value) for their own shop.
3. Replay that exact body and HMAC to the app's webhook endpoint, but with the `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) header rewritten to a victim shop's domain.

`HmacValidator.validate` recomputes the HMAC over the (unchanged) body with the shared secret and it matches, so `Errors::InvalidWebhookError` is never raised. `Registry.process` then calls the app's handler with `shop: request.shop` equal to the attacker-chosen victim domain, even though the signature never covered that value. The identity binding that should hold — "shop the webhook is authenticated for" == "shop the handler is told the data belongs to" — is broken, because the HMAC never authenticates the `shop` field at all.

### Impact Explanation
This crosses a tenant boundary: an attacker with no access to the victim shop or its access token can cause the host application to process arbitrary, attacker-controlled webhook payloads (order data, app-uninstall/GDPR events, etc.) as if they originated from a victim shop, since the gem hands the handler an unauthenticated `shop` value alongside an authenticated body. Any host logic that keys persistence, authorization, or side effects off `WebhookMetadata#shop` (which is exactly the documented use of this API — see `Registry.process`'s construction of `WebhookMetadata`) is exposed to cross-tenant data injection/confusion. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is high: the only prerequisite is the ability to install the target app on any shop (something any internet user can do for a public app, e.g. via a free/dev store), then capture and replay one legitimate webhook body/HMAC pair with a modified header value — no secret material, access token, or privileged account is required, and no TLS interception is needed since the attacker is simply crafting their own outbound HTTP request to the app's public webhook endpoint.

### Recommendation
Bind the `shop` (and ideally `topic`, `webhook_id`, `api_version`) to the signed content, or otherwise verify that the shop asserted in the header matches a shop this specific webhook secret is scoped to (e.g. per-shop verification, or including the header values in the signable string if using per-app-shared secrets). At minimum, document that `request.shop` must not be trusted as an authenticated identifier by consuming applications unless independently corroborated (e.g. cross-checked against a known/installed shop list), and consider raising `Errors::InvalidWebhookError` when the `shop` header does not correspond to a shop known to have a valid installation for the app instance processing the request.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` (their own store).
2. Shopify sends a real webhook, e.g.:
   ```
   POST /webhooks HTTP/1.1
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: <valid_hmac_for_body>
   X-Shopify-Shop-Domain: attacker-shop.myshopify.com
   Body: {"id": 1, "note": "..."}
   ```
   Attacker records the exact `Body` and `X-Shopify-Hmac-Sha256` value.
3. Attacker replays the identical request to the same app endpoint, changing only the shop header:
   ```
   POST /webhooks HTTP/1.1
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: <same_valid_hmac_for_same_body>
   X-Shopify-Shop-Domain: victim-shop.myshopify.com
   Body: {"id": 1, "note": "..."}
   ```
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because the body is unchanged and `Context.api_secret_key` is shared across all shops for this app.
5. The registered handler is invoked with `WebhookMetadata#shop == "victim-shop.myshopify.com"`, even though nothing about that value was ever authenticated, demonstrating the cross-tenant attribution spoof.

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
