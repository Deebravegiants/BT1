### Title
Webhook `shop` Identity Is Not Covered by the HMAC Signature, Allowing Cross-Tenant Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by HMAC-validating the raw request body, then hands the handler a `shop` value that is read from an HTTP header which is never part of the signed data. An attacker who possesses one valid `(raw_body, hmac)` pair (trivially obtainable, since every merchant using the app receives real, validly-signed webhooks for their own store) can replay that exact body/HMAC pair while substituting the `shopify-shop-domain` header for a victim shop, and the gem will accept it as authentic and dispatch it to the handler as if it belonged to the victim tenant.

### Finding Description
`Webhooks::Request#to_signable_string` only returns the raw body: [1](#0-0) 

The `shop` accessor is derived independently from a header that is not part of that signable string: [2](#0-1) 

`Registry.process` validates the HMAC over the request (i.e., over the body only) and then constructs `WebhookMetadata` using `request.shop`, treating it as an authenticated tenant identifier even though it was never bound by the signature: [3](#0-2) 

The identity binding that should hold is:
`shop value trusted by the handler == shop value covered by the HMAC`

but in this implementation:
`shop value trusted by the handler (HTTP header) != bytes verified by HmacValidator (raw body only)`

This exactly matches the "field acted on but not covered by the HMAC" analog: the `shop` field, which downstream handler code uses as the tenant identity, is not included in `to_signable_string`, so it can be freely swapped by anyone who can supply the raw HTTP request while reusing a legitimately-signed body.

### Impact Explanation
An unprivileged user who is a legitimate merchant of the app (or anyone who otherwise obtains one valid `(body, hmac)` pair — these are not secret and pass through untrusted infrastructure, logs, browser devtools when previewed, etc.) can replay that pair with an arbitrary `shopify-shop-domain` header. Because `Registry.process` never cross-checks `shop` against anything covered by the signature, the app's webhook handler will execute business logic believing the payload originated from a different, victim tenant. Depending on how the host app's handler uses `data.shop` (e.g., to select which merchant record to update/delete, or to authorize actions), this enables cross-tenant data corruption or a cross-tenant trust confusion — matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is meaningful but not trivial: the attacker needs at least one legitimately-signed `(raw_body, hmac)` pair, which is easy to obtain if the attacker is themselves a merchant of the app (every real merchant receives real, validly-signed webhooks for their own shop). No access to `api_secret_key` or any privileged credential is required — only the ability to send an HTTP request with modified headers to the app's publicly reachable webhook endpoint.

### Recommendation
Include the shop domain (and ideally topic/webhook id) inside the data that is HMAC-verified, or otherwise cryptographically bind the `shopify-shop-domain` header to the signed payload before trusting it in `WebhookMetadata`. At minimum, the gem should document/enforce that callers must independently verify `data.shop` against a known, provisioned shop (e.g., an existing offline session) rather than treating the header as authenticated by `HmacValidator.validate`.

### Proof of Concept
1. Merchant A installs the app; the app registers a webhook endpoint.
2. Shopify sends a real webhook to the endpoint for shop A with a valid `x-shopify-hmac-sha256` computed over the raw body.
3. Attacker (Merchant A) captures this exact `(raw_body, hmac)` pair.
4. Attacker resends the identical raw body and HMAC header to the app's webhook endpoint, but sets `shopify-shop-domain: victim-shop.myshopify.com`.
5. `Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks the HMAC against `@raw_body` — this still passes because the body/HMAC pair is unmodified.
6. `request.shop` returns `victim-shop.myshopify.com`, and `WebhookMetadata` is built and handed to the app's handler as if it were an authentic event for the victim shop. [4](#0-3) [5](#0-4)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
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
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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
