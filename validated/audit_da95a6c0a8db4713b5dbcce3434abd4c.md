### Title
Webhook `shop-domain` header is trusted for tenant routing but is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` authenticates an inbound webhook solely by HMAC-signing the raw request body, but the `shop` (tenant identifier) that is handed to the application's webhook handler is read from the unsigned `X-Shopify-Shop-Domain` header. Anyone who can obtain one genuine, HMAC-valid webhook payload for *any* shop (including their own free/dev shop) can replay it to the app's webhook endpoint with the `shop-domain` header swapped to a victim shop, and `ShopifyAPI::Webhooks::Registry.process` will accept it as authentic and dispatch it to the handler as if it originated from the victim tenant.

### Finding Description
The identity binding that should hold is:

```
shop_header_used_by_handler == shop_that_was_authenticated_by_the_HMAC
```

`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body: [1](#0-0) 

while `#shop` is read directly from the `shopify-shop-domain` / `x-shopify-shop-domain` header, entirely outside the signed material: [2](#0-1) [3](#0-2) 

`ShopifyAPI::Utils::HmacValidator.validate` only ever checks `verifiable_query.to_signable_string` against the HMAC — for a webhook `Request`, that is the raw body only: [4](#0-3) 

`ShopifyAPI::Webhooks::Registry.process` performs exactly this check and, once it passes, forwards `request.shop` (unauthenticated) straight into the handler's `WebhookMetadata`: [5](#0-4) 

Because the shop header is never part of the signed bytes, the HMAC only proves "this body was produced by Shopify (or someone with the secret) for *some* shop" — it does not prove *which* shop. An attacker who legitimately installs the same app on their own shop (no privileged credentials needed — this is exactly the "unprivileged internet user" scenario) will receive genuine webhooks (e.g. `app/uninstalled`, or any topic whose body is empty/generic such as `{}`) signed with the app's real secret for their own tenant. They can capture that raw body + HMAC and replay it to the same webhook endpoint while substituting the `X-Shopify-Shop-Domain` header for a victim shop's domain. `Utils::HmacValidator.validate` still succeeds (body+HMAC pair is unchanged), and `Registry.process` calls the handler with `shop: <victim shop>`.

### Impact Explanation
Most host applications key their tenant lookup, session revocation, or data-mutation logic directly off `WebhookMetadata#shop` (e.g. "find session/shop record by domain and act on it"). Since this gem is the trust boundary that is supposed to guarantee "this webhook data really pertains to this shop," an attacker can use their own legitimately-issued webhook to make the app perform tenant-scoped actions (e.g. disable/uninstall handling, config wipes, cache invalidation, GDPR-style redaction flows) against a shop they do not own and never authenticated as. This is a cross-tenant identity-binding break stemming directly from this gem's `Webhooks::Request`/`Registry` design, not from host-application misuse of a documented API — the gem itself exposes `#shop` as a "verified" webhook attribute without binding it to the signature it validates.

### Likelihood Explanation
Trivial and cheap to execute: any user can create a free development store, install the target app to receive one genuine webhook, and then replay that captured, still-validly-signed body against the same endpoint with a different `shop-domain` header. No access token, `client_secret`, or privileged account is required — only a body/HMAC pair the attacker legitimately received for their own shop.

### Recommendation
Include the shop domain (and ideally topic/webhook id) inside the signed material, or otherwise cryptographically bind the `shop-domain` header to the HMAC-validated body before it is trusted — e.g. compute/verify the HMAC over `"#{shop}\n#{topic}\n#{raw_body}"`, or require host apps to independently verify that the shop asserted in the header matches a shop for which the app currently holds an active, previously-OAuth-authenticated session before acting on the webhook. At minimum, document prominently that `Request#shop` is unauthenticated and must not be used as the sole tenant selector.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` (no special privileges required).
2. Shopify sends a genuine webhook, e.g. topic `app/uninstalled` with body `{}`, to the app's registered webhook endpoint, signed with:
   ```
   hmac = Base64.encode64(OpenSSL::HMAC.digest("sha256", api_secret_key, "{}"))
   headers = {
     "x-shopify-topic" => "app/uninstalled",
     "x-shopify-hmac-sha256" => hmac,
     "x-shopify-shop-domain" => "attacker.myshopify.com",
     ...
   }
   ```
3. Attacker captures this exact `raw_body` ("{}") and `hmac` value.
4. Attacker resends the same POST to the app's webhook endpoint, keeping `raw_body` and `hmac` identical, but changes the header to `"x-shopify-shop-domain" => "victim.myshopify.com"`.
5. `ShopifyAPI::Webhooks::Request.new(raw_body: "{}", headers: forged_headers)` produces a request whose `hmac` still matches (`to_signable_string` only depends on `raw_body`):
   `ShopifyAPI::Utils::HmacValidator.validate(request) # => true`
6. `ShopifyAPI::Webhooks::Registry.process(request)` passes and calls the app's `app/uninstalled` handler with `WebhookMetadata.new(shop: "victim.myshopify.com", topic: "app/uninstalled", body: {}, ...)`, causing the host app to treat this as an authentic uninstall/cleanup event for `victim.myshopify.com` even though Shopify never sent this webhook for that shop.

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

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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
