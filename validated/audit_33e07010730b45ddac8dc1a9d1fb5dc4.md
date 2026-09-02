### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant shop spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` identity that gets passed to the host application's webhook handler entirely from the unauthenticated `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header, while the HMAC that `ShopifyAPI::Utils::HmacValidator` verifies only covers the raw request body.

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Request#shop` is read straight off the `shopify-shop-domain`/`x-shopify-shop-domain` header with no further validation [2](#0-1) .

`Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)`, which only checks `computed_signature` against the body-derived signable string using `HMAC-SHA256(api_secret_key, raw_body)` [3](#0-2) . If that check passes, `Registry.process` immediately builds `WebhookMetadata` using `request.shop` and hands it to the app's handler [4](#0-3) .

This breaks the intended identity binding: **shop authenticated by the HMAC (implicitly "whatever shop generated this HMAC-valid body") ≠ shop asserted to the handler (the raw, attacker-controllable `shop-domain` header)**. Because the header is excluded from the signed content, any two values `(raw_body, hmac)` that are valid for the app's shared secret remain valid for *any* `shop-domain` header value — the shop field can be swapped freely without invalidating the signature.

This is directly exploitable by an unprivileged attacker who is simply a legitimate merchant of the target app (installing any Shopify app to receive its genuine webhooks is available to any internet user for free, no special privilege required). Once that attacker's own shop triggers a webhook (e.g. `orders/create`, `app/uninstalled`, `customers/data_request`), Shopify sends a request to the app containing a body and a valid HMAC computed with the app's `api_secret_key` — an attacker can capture this genuine `(raw_body, hmac)` pair from their own store. They can then replay that exact `raw_body`/`hmac` pair to the app's webhook endpoint while substituting the `shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` still returns `true` (the raw body/HMAC pair is genuinely valid), and `Registry.process` will invoke the handler believing this event legitimately originates from the victim shop [4](#0-3) .

### Impact Explanation
Because host applications are documented to key their business logic on `data.shop` from `WebhookMetadata` (per `docs/usage/webhooks.md`, apps look up/act on records keyed by `data.shop`), an attacker can trigger the app's webhook handler logic *as if* it came from a shop they do not own or control. Depending on the topic abused (e.g. `app/uninstalled` semantics, `customers/redact`/`customers/data_request` mandatory topics, or any custom topic), this can force the application to perform tenant-scoped mutations (session/token teardown, data deletion, cache invalidation, GDPR-type actions) against a victim shop that never actually sent that webhook. This is a cross-tenant identity-binding break: the shop the HMAC vouches for (the app's own dev/attacker shop) does not equal the shop the application acts upon (the spoofed victim shop).

### Likelihood Explanation
Likelihood is non-trivial: any internet user can install the target app on a free/dev Shopify store, observe or trigger a webhook to obtain a valid `(raw_body, hmac)` pair signed with the app's shared secret, and then send an HTTP request directly to the app's public webhook endpoint with an altered `shop-domain` header. No access token, `client_secret`, or privileged account is required — only the ability to receive one legitimate webhook from the target app.

### Recommendation
Include the shop domain (and other identity-relevant headers) inside the HMAC-signed content, or independently verify that `request.shop` corresponds to an actual installed/authorized shop (e.g., cross-check against a known session/shop record) before dispatching to the handler, rather than trusting the raw header value once only the body's HMAC has been validated.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` and receives a genuine webhook, e.g. for `orders/create`, with headers:
   - `x-shopify-hmac-sha256: <valid HMAC of raw_body computed with app's api_secret_key>`
   - `x-shopify-shop-domain: attacker-shop.myshopify.com`
   - `x-shopify-topic: orders/create`
   and body `raw_body`.
2. Attacker resends this exact request to the app's public webhook endpoint, changing only the header:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
   (raw_body and hmac unchanged).
3. `ShopifyAPI::Webhooks::Request#hmac` and `#to_signable_string` compute/return the same values as before (body unchanged) [5](#0-4) .
4. `Utils::HmacValidator.validate` recomputes `HMAC(api_secret_key, raw_body)` and compares via `OpenSSL.secure_compare` — this still matches, since the header change did not alter `raw_body` [3](#0-2) .
5. `Registry.process` passes validation and calls `handler.handle(data: WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", ...))` [4](#0-3) , causing the app to process the attacker's event data as if it came from the victim shop.

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
