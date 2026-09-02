### Title
Webhook `shop` domain is not covered by HMAC, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw HTTP body only, while the `shop` identity used by `ShopifyAPI::Webhooks::Registry.process` to route webhook data to a handler is read from a separate, unsigned HTTP header. The HMAC check therefore validates a different set of bytes than the identity field the handler actually trusts.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is parsed independently from the `shopify-shop-domain`/`x-shopify-shop-domain` header, with no cryptographic tie to the signed body: [2](#0-1) 

`Utils::HmacValidator.validate` only recomputes and compares the HMAC over `verifiable_query.to_signable_string` (the raw body) against the `hmac` header — it never incorporates `shop`: [3](#0-2) 

`Registry.process` performs exactly this body-only HMAC check and then immediately trusts `request.shop` to build the tenant-identifying `WebhookMetadata` passed to the app's handler: [4](#0-3) 

Because the app's `client_secret` (used as the HMAC key) is shared across every shop that has the app installed, any merchant who legitimately installs the app can generate a request body with a genuine, valid HMAC signature (e.g., by triggering a real webhook event, such as `orders/create`, on their own store). The equality the code is supposed to enforce is:
`shop that produced/authorizes the signed bytes == shop attributed to the event`.
In reality the code only proves `raw_body is unmodified`, and separately trusts whatever `shop-domain` header value accompanies that same valid signature. An attacker can take a real, validly-signed webhook payload from their own shop and resend it to the app's webhook endpoint with the `shop-domain` header rewritten to a victim shop, since that header is completely outside the signed bytes. `HmacValidator.validate` will return `true` for this forged request, and `Registry.process` will hand the attacker-controlled body to the host app's handler labeled as coming from the victim shop.

### Impact Explanation
This crosses a tenant boundary: the gem's own webhook signature check offers no protection against the `shop` identity being swapped for another tenant, and the deceived host application will process attacker-controlled data as if it originated from a different, victim merchant. Depending on what the host app's webhook handler does with `data.shop` (e.g., attributing orders, syncing inventory, updating billing/subscription state, or writing to per-shop records keyed by this value), this enables cross-tenant data injection/corruption despite the HMAC check nominally "passing."

### Likelihood Explanation
Any actor can obtain a free/developer store, install the target app, and receive genuinely signed webhook deliveries at will (e.g., by creating an order, updating a product, etc.). Capturing one such delivery and replaying it with a modified `shop-domain` header requires no secrets and no privileged access — only the ability to install the app on one's own store, which is the normal, expected way of using it.

### Recommendation
Bind the `shop` field into the value that is HMAC-verified, or otherwise establish an independent trust anchor for the shop identity before dispatching to handlers:
- Require host applications (and ideally enforce in the gem) to cross-check `request.shop` against a shop that is already known/registered (e.g., an existing offline session for that shop) before trusting `WebhookMetadata#shop`.
- Where possible, include the shop domain as part of the signable content, or validate it out-of-band against Shopify's known list of installed shops for the app.
- Document explicitly in `Registry.process`/`Request` that `shop` is not authenticated by the HMAC and must not be used as the sole tenant-selection key by consuming applications.

### Proof of Concept
1. Attacker installs the target Shopify app on their own development store `attacker-shop.myshopify.com`.
2. Attacker triggers a webhook event (e.g., creates an order), and Shopify delivers a POST request to the app's webhook endpoint with headers `x-shopify-hmac-sha256: <valid HMAC over raw body>` and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker intercepts this request, keeps the body and `x-shopify-hmac-sha256` value unchanged, but replaces `x-shopify-shop-domain` with `victim-shop.myshopify.com`, and resends it to the same endpoint.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC solely over `raw_body` — see `lib/shopify_api/webhooks/request.rb:35-38` and `lib/shopify_api/utils/hmac_validator.rb:26-31` — and it matches, so validation succeeds.
5. `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)` is built with `shop == "victim-shop.myshopify.com"` (see `lib/shopify_api/webhooks/registry.rb:198-199`) and passed to the host application's handler, which processes attacker-supplied data as if it belonged to the victim shop.

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
