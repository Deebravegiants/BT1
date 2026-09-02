### Title
Webhook `X-Shopify-Shop-Domain` Header Not Covered by HMAC Signature — Cross-Tenant Shop Spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` value used by webhook handlers from the unauthenticated `X-Shopify-Shop-Domain`/`shopify-shop-domain` header, but `HmacValidator` only verifies the raw request body against `X-Shopify-Hmac-Sha256`. The header identifying which tenant a webhook belongs to is not part of the signed material, breaking the binding between "shop the HMAC was computed for" and "shop the application acts on."

### Finding Description
`Registry.process` gates webhook processing solely on `Utils::HmacValidator.validate(request)`: [1](#0-0) 

`HmacValidator.validate` computes the signature exclusively from `verifiable_query.to_signable_string`: [2](#0-1) 

For `Webhooks::Request`, `to_signable_string` returns only the raw HTTP body — none of the Shopify headers (topic, shop-domain, webhook-id, api-version) are included in the signable material: [3](#0-2) 

Yet `request.shop`, which is read straight from the unauthenticated header, is what gets forwarded to the app's handler as the identity of the tenant the webhook belongs to: [4](#0-3) [5](#0-4) 

The equality that should hold is: `shop_bound_by_HMAC == shop_the_app_acts_on`. Instead the gem enforces only `HMAC(body) == received_hmac`, while `shop_the_app_acts_on = header["shop-domain"]` (unauthenticated). Since the HMAC secret (`api_secret_key`) is shared across all shops that have the app installed, any unprivileged internet user who can install the app on a shop they control receives legitimately-HMAC-signed webhook deliveries for that shop. That attacker can capture one such delivery (raw body + valid `X-Shopify-Hmac-Sha256`) and replay it to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header rewritten to a victim shop's domain. `HmacValidator.validate` still succeeds (it never looked at the shop header), and `Registry.process` invokes the handler with `WebhookMetadata.new(... shop: request.shop ...)` reporting the victim shop, letting the attacker inject or replay fabricated data attributed to a tenant they do not control.

### Impact Explanation
This crosses a tenant boundary purely through data the gem itself never authenticates: the application logic that keys persistence/side effects off `shop` (e.g., updating merchant records, deleting data on `shop/redact`, or triggering fulfillment logic) can be made to run against an arbitrary victim shop identifier while carrying an attacker-fully-controlled body. This is a cross-tenant access primitive attributable to the gem's `HmacValidator`/`Webhooks::Request` design, independent of how the host application implements its webhook handler, since the gem is what asserts "this HMAC-validated request is a legitimate webhook for `request.shop`."

### Likelihood Explanation
Any developer/merchant can install the target app on a shop they control to receive real, validly-signed webhook deliveries, then trivially replay the captured HTTP request with a modified shop header value. No access token, `client_secret`, or privileged account is required — only the unprivileged ability to install the app on one's own store, which is normal merchant self-service.

### Recommendation
Include the shop-identifying header (and ideally topic/webhook-id) as part of the HMAC-covered material, or otherwise validate that `request.shop` corresponds to a shop the receiving application actually expects to receive webhooks for before dispatching to handlers — Shopify's own webhook HMAC is computed over the raw body only by design, so the safer fix is for the gem to require/verify the shop domain out-of-band (e.g., cross-check against the app's known installed-shop list) rather than trusting the unauthenticated header as the tenant identity passed to handlers.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`.
2. Attacker triggers an event (e.g., `orders/create`) on their own shop and captures the raw webhook POST, including a valid `X-Shopify-Hmac-Sha256` header computed by Shopify using the app's `api_secret_key`.
3. Attacker replays the exact same body and HMAC header to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` succeeds because it only checks `HMAC(raw_body)`, which is unchanged.
5. `Registry.process` calls the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker-controlled JSON>, ...)`, causing the application to process attacker-controlled data as if it originated from the victim shop.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
