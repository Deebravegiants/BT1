### Title
Webhook shop identity is not bound to the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop`, `topic`, `api_version`, and `webhook_id` fields — which are trusted and passed downstream to the app's webhook handler as the tenant identity — are read from unauthenticated HTTP headers that are never covered by that signature.

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `HmacValidator.validate` checks the received `hmac` header against a signature computed solely over that signable string [2](#0-1) . However, `Request#shop`, `#topic`, `#api_version`, and `#webhook_id` are all pulled directly from HTTP headers (`shopify-shop-domain`, `shopify-topic`, etc.) that are not part of the signed bytes [3](#0-2) .

`Registry#process` validates the HMAC and then immediately forwards `request.shop`, `request.topic`, and `request.webhook_id` into `WebhookMetadata`, which is handed to the app's registered handler as the trusted tenant/topic context: [4](#0-3) 

The equality the gem should enforce is: **shop bytes covered by HMAC == shop bytes acted upon by the handler**. Instead, the gem enforces only "body bytes covered by HMAC == body bytes parsed," while the `shop`/`topic`/`webhook_id` headers used for tenant routing are completely outside that binding.

### Impact Explanation
An unprivileged internet user who has legitimate access to any single Shopify shop (e.g., their own free development store) can trigger a real webhook delivery to an app they control, capturing a genuine `(raw_body, hmac)` pair signed by the app's `client_secret`. Because the signature never covers the `shop-domain` header, the attacker can replay that exact body and HMAC to the target app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header for a victim shop's domain (and/or a different topic/webhook-id). `HmacValidator.validate` still returns `true` since only the body bytes matter, and `Registry#process` dispatches the forged data to the handler as if it genuinely originated from the victim shop. This is a cross-tenant access vulnerability: the app's business logic (data deletion/redaction handlers, order/customer sync, per-shop state updates, etc.) is invoked under an attacker-chosen shop identity without ever needing the app's `client_secret`, an access token, or any privileged credential.

### Likelihood Explanation
Likelihood is high: obtaining a valid `(raw_body, hmac)` pair requires nothing more than installing the app on any shop the attacker controls and letting a normal webhook fire — a fully unprivileged, self-service action. Replaying the captured request with a modified `shop-domain` header against the same public webhook endpoint requires no additional secrets and no network-level MITM.

### Recommendation
Bind the header fields that are treated as trusted identity (`shop`, `topic`, `webhook_id`, `api_version`) into the signed material, or otherwise cryptographically tie them to the payload before HMAC validation — e.g., include them in `to_signable_string`, or independently verify the shop against a value obtained through an authenticated channel (such as a known/expected shop list or session lookup) rather than trusting the raw header value once the body-only HMAC passes.

### Proof of Concept
1. Install the app under attacker-owned shop `attacker.myshopify.com`; trigger any subscribed webhook topic (e.g. `orders/create`) so Shopify delivers a POST to the app with headers `X-Shopify-Shop-Domain: attacker.myshopify.com`, `X-Shopify-Hmac-Sha256: <valid_hmac>`, and body `B`.
2. Capture `B` and `<valid_hmac>` (trivial, since the attacker owns the receiving endpoint/logs).
3. Send a new POST request to the same webhook endpoint with the identical body `B` and `X-Shopify-Hmac-Sha256: <valid_hmac>`, but change `X-Shopify-Shop-Domain` to `victim.myshopify.com`.
4. `Utils::HmacValidator.validate(request)` returns `true` because it only checks `B` against `<valid_hmac>` [5](#0-4) ; `Registry#process` then invokes the handler with `shop: "victim.myshopify.com"`, letting the attacker inject forged data attributed to the victim tenant.

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
