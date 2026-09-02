### Title
Webhook shop-tenant identity spoofing via unauthenticated `shop-domain` header not covered by HMAC - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/utils/hmac_validator.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw body only, while the shop-tenant identity (`shop`) used downstream by `Registry.process` to dispatch the webhook to the host app's handler is read from an unauthenticated HTTP header. An unprivileged attacker who controls their own Shopify store (a normal app install, no special privilege) can capture one legitimate webhook delivery and replay it with a forged `shop-domain` header pointing at a victim tenant, while keeping the same body/HMAC pair, causing the app to process attacker-controlled webhook data under the victim's tenant identity.

### Finding Description
`Request#hmac` and `Request#to_signable_string` derive the signable content solely from the raw body: [1](#0-0) 

`shop` (and `topic`, `webhook_id`, `api_version`) are pulled straight from HTTP headers that are never part of the signed payload: [2](#0-1) 

`Utils::HmacValidator.validate` verifies the HMAC exclusively against `to_signable_string` (the raw body), independent of any header value: [3](#0-2) 

`Registry.process` treats a successful HMAC check as authenticating the whole request, then forwards the unauthenticated `request.shop` header value straight into the app's handler as the trusted tenant identity: [4](#0-3) 

The intended binding is: `shop header == shop attested by the app's HMAC secret`. In reality the HMAC only binds the body bytes; the shop header can be swapped freely without invalidating the signature, breaking that equality. Because the webhook signing secret (`Context.api_secret_key`, the app's `client_secret`) is the same for every shop that installs the app, any merchant who installs the app on their own store legitimately receives valid `(body, hmac)` pairs signed with that shared secret. That merchant can then resend the identical body and HMAC to the app's webhook endpoint while substituting the `shopify-shop-domain` (or `x-shopify-shop-domain`) header with any other shop's domain, and the check in `HmacValidator.validate` still passes.

### Impact Explanation
This crosses a tenant boundary: the host application's webhook handler receives `WebhookMetadata` with an attacker-chosen `shop` value alongside attacker-influenced webhook body content, but treats it as an authenticated event for that shop (per the documented handler contract shown in `docs/usage/webhooks.md`, `data.shop` is the trusted "shop domain of the webhook"). Depending on how the host app uses `data.shop` (e.g., looking up tenant records, writing order/customer data, triggering fulfillment, billing, or session-bound side effects), this enables cross-tenant data injection/corruption or triggering of actions attributed to a shop the attacker does not own. This matches the Critical "cross-tenant access" category, since it requires no access token, no `api_secret_key`, and no privileged account — only an ordinary, unprivileged app installation by the attacker on their own store.

### Likelihood Explanation
Any account that can install the target app (a completely unprivileged action available to any merchant/internet user for public apps) can obtain the shared-secret-signed `(body, hmac)` pair from their own legitimate webhook deliveries, then replay it against the app's public webhook endpoint with a modified shop header. No secret material, tokens, or victim cooperation are required.

### Recommendation
Bind the shop identity into the authenticated payload before dispatching to handlers: include the `shop-domain` (and ideally `topic`/`webhook-id`) header value in the signable string used for HMAC verification, or independently verify that `request.shop` corresponds to a shop with an active, previously-established session/subscription for that specific webhook (e.g., checking the shop against the webhook registration/subscription that was created for it) before invoking the handler with that shop's identity.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` (normal unprivileged install flow).
2. Shopify delivers a legitimate webhook to the app, e.g.:
   - Headers: `X-Shopify-Shop-Domain: attacker.myshopify.com`, `X-Shopify-Hmac-SHA256: <base64 hmac of body>`, `X-Shopify-Topic: orders/create`
   - Body: `{"id":1,"note":"hello"}`
3. Attacker captures this exact `(body, hmac)` pair (trivial, since it's their own store's traffic).
4. Attacker sends a new POST to the app's public webhook endpoint with the identical body and `X-Shopify-Hmac-SHA256` value, but replaces the header:
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com`
5. App code does:
   ```ruby
   ShopifyAPI::Webhooks::Registry.process(
     ShopifyAPI::Webhooks::Request.new(raw_body: request.raw_post, headers: request.headers.to_h)
   )
   ```
6. `HmacValidator.validate` recomputes `OpenSSL::HMAC.hexdigest(secret, raw_body)` — unaffected by the header change — and returns `true`.
7. `Registry.process` calls `handler.handle(data: WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: {"id"=>1,"note"=>"hello"}, ...))`, and the host app processes attacker-supplied order data as belonging to the victim tenant.

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
