### Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook using only the raw request body, then forwards a `shop` value taken from an HTTP header that is never included in that signature. Because the app's `api_secret_key` is shared across every shop that installs the app, any shop owner who can trigger a legitimately-signed webhook for their own store obtains a `(body, hmac)` pair that remains valid regardless of which `shop-domain` header accompanies it. Replaying that pair with a different `shop-domain` header lets an attacker make the app process webhook data while `WebhookMetadata#shop` claims to be a different, victim tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is not part of the signed content: [2](#0-1) 

`HmacValidator.validate` computes and compares the HMAC solely over `verifiable_query.to_signable_string` (i.e., the body): [3](#0-2) 

`Registry.process` performs this HMAC check and then, on success, dispatches the handler using `request.shop` as the tenant identity, without any additional binding between the authenticated bytes and the claimed shop: [4](#0-3) 

The identity binding that should hold is:
`HMAC-authenticated bytes == bytes that determine the tenant (shop) the payload is attributed to`

Here, the equality does not hold: the HMAC only authenticates `raw_body`, while `shop` (the tenant-selection field consumed by `WebhookMetadata` and, in turn, by the host application's per-shop business logic) is taken from unauthenticated header bytes.

### Impact Explanation
Because `Context.api_secret_key` is a single app-wide secret shared by every installed shop, a valid `(body, hmac)` pair generated for the attacker's own store's webhook remains a valid pair for any `shop-domain` value. An attacker who controls one shop that has installed the target app can:
1. Trigger (or wait for) a webhook delivery for their own shop and capture the raw body and its `X-Shopify-Hmac-Sha256` value.
2. Replay that exact body/HMAC to the app's webhook endpoint while substituting `X-Shopify-Shop-Domain` with a victim shop's domain.
3. `Registry.process` will validate successfully (the HMAC only checks the body) and call the app's handler with `WebhookMetadata#shop == victim-shop`, causing the host application to attribute attacker-controlled data to another tenant.

This crosses a tenant boundary using only the identity fields this gem exposes to the handler, matching the "cross-tenant access" impact category, since the gem itself is what asserts the authenticated identity of the webhook to the app.

### Likelihood Explanation
Exploitation requires only that the attacker be able to install the target app on a shop they control (a normal, unprivileged action for any Shopify merchant/dev-store owner) and be able to send an arbitrary HTTP POST to the app's public webhook endpoint — no leaked secret or privileged access is needed. The only constraint is finding a webhook topic whose body content is attacker-influenceable or predictable/replayable (e.g., a webhook fired from actions the attacker fully controls on their own store), which is broadly achievable for many webhook topics (e.g., `app/uninstalled`, `products/create`, custom metafield webhooks, etc., where the attacker fully controls the resource and thus the body).

### Recommendation
Bind the `shop` identity to the authenticated bytes, e.g., by including the `shop-domain` header (and other identity-relevant headers used downstream) in the HMAC-signed payload, or by validating that the returned `shop` is independently confirmed (e.g., cross-checked against the session/store the caller expects) before dispatching to the handler. At minimum, document prominently that `WebhookMetadata#shop` is not cryptographically bound to the signature and must not be trusted as an authenticated tenant identifier without further verification by the host app.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` (app's `api_secret_key` is shared across all shops).
2. Attacker triggers a webhook event on their own shop with an attacker-controlled/known body, e.g. an empty-body-equivalent event, and captures the resulting `X-Shopify-Hmac-Sha256` value that Shopify computed with the shared app secret.
3. Attacker POSTs to the victim app's webhook endpoint with:
   - `X-Shopify-Topic`: same topic
   - `X-Shopify-Hmac-Sha256`: the captured, valid HMAC
   - `X-Shopify-Shop-Domain`: `victim-shop.myshopify.com`
   - Body: the exact captured raw body
4. `ShopifyAPI::Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb:189-199`) calls `Utils::HmacValidator.validate(request)`, which passes because it only checks the body/HMAC pair.
5. The registered handler is invoked with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)`, even though nothing about the request was ever verified as originating from, or on behalf of, `victim-shop.myshopify.com`.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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
