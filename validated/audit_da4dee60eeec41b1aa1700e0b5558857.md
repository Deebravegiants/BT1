## Title
Webhook HMAC verification only covers the raw body, letting an attacker spoof the `shop`, `topic`, and `webhook_id` headers to attribute forged events to another tenant - (`File: lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so the HMAC-SHA256 signature that `Webhooks::Registry.process` verifies covers *nothing but the JSON body*. The `shopify-shop-domain`, `shopify-topic`, and `shopify-webhook-id` headers — which the registry trusts to route the request and to identify the acting tenant — are read straight from unauthenticated HTTP headers and never bound into the signed payload.

### Finding Description
`Utils::HmacValidator.validate` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it against the `hmac` value on the object [1](#0-0) . For webhooks, `to_signable_string` is defined as simply the raw request body: [2](#0-1) 

Meanwhile `shop`, `topic`, and `webhook_id` are pulled directly from HTTP headers with no cryptographic binding to the signature: [3](#0-2) 

`Registry.process` verifies only the HMAC and then dispatches purely on the unauthenticated `topic`/`shop` values: [4](#0-3) 

The identity binding that should hold is:
```
HMAC_valid(body) == HMAC_valid(body) AND shop_header == shop_that_produced(body)
```
but the gem only proves the left side. Because the same app `client_secret` is used to sign webhooks for *every* installed shop, any shop running the app can legitimately receive a genuine `(body, hmac)` pair from Shopify, then replay that exact body/HMAC pair to the app's webhook endpoint while substituting `shopify-shop-domain` (and/or `shopify-topic`, `shopify-webhook-id`) headers for a different tenant. `HmacValidator.validate` still passes because it only checks the body, and `Registry.process` happily hands the forged `shop` value to the registered handler via `WebhookMetadata` [5](#0-4) .

### Impact Explanation
This lets an unprivileged internet user who legitimately installs the app on their own store (attacker-controlled shop A) forge webhook events that the host application will process as if they originated from shop B (`shopify-shop-domain: shop-b.myshopify.com`), and/or under a different `topic`. Any host logic keyed on `WebhookMetadata#shop` for tenant separation (e.g., updating per-shop data, honoring GDPR `customers/redact`/`shop/redact` mandatory topics, billing events) can be manipulated across tenants — this is a cross-tenant access primitive attributable directly to this gem's signature-verification design.

### Likelihood Explanation
Exploitation only requires the attacker to run the app on any shop they control (a normal, unprivileged onboarding flow) and to be able to POST to the app's public webhook endpoint — no access token, `client_secret`, or privileged account is required. Obtaining at least one valid `(raw_body, hmac)` pair is trivial since Shopify sends the attacker's own shop legitimate webhooks continuously.

### Recommendation
Bind the identity fields into the signed payload verification, e.g., include `shop`, `topic`, and `webhook_id` in `to_signable_string` (or otherwise cryptographically bind them), or require the caller/host framework to independently authenticate the shop before trusting `WebhookMetadata#shop`. At minimum, document and enforce that `shop`/`topic` headers must not be trusted independent of application-level shop verification (e.g., checking the shop exists in the app's own session store) before acting on webhook data.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and receives a genuine webhook, e.g. an `app/uninstalled` POST with body `{}` and header `shopify-hmac-sha256: <valid-hmac-of-{}>`.
2. Attacker replays the identical body and HMAC header to the app's public webhook endpoint, but sets:
   - `shopify-shop-domain: victim-shop.myshopify.com`
   - `shopify-topic: shop/redact` (or any topic the app has registered a handler for)
3. `ShopifyAPI::Webhooks::Request.new(raw_body: "{}", headers: forged_headers)` is constructed; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only hashes `"{}"` [2](#0-1) .
4. The registered handler for `shop/redact` executes with `WebhookMetadata.new(topic: "shop/redact", shop: "victim-shop.myshopify.com", ...)`, causing the host app to act (e.g., delete/redact data) as though the event genuinely came from Shopify for `victim-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

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
