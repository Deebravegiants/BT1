## Title
Webhook `shop` (and `topic`/`webhook_id`) header is not covered by the HMAC signature, allowing cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so the HMAC signature validated by `ShopifyAPI::Utils::HmacValidator.validate` binds only the request body. The `shop-domain`, `topic`, and `webhook-id` headers are read directly from the unauthenticated HTTP headers and passed downstream to the app's webhook handler without being part of the signed material, breaking the identity binding: `shop_that_produced_the_signed_body == shop_attributed_to_the_webhook`.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` validates a webhook solely via: [1](#0-0) 

`Utils::HmacValidator.validate` computes/verifies the HMAC over `verifiable_query.to_signable_string`: [2](#0-1) 

For `Webhooks::Request`, `to_signable_string` returns **only** the raw body — none of the Shopify headers (`shop`, `topic`, `webhook_id`, `api_version`) are included in the signed string: [3](#0-2) 

Because the shared `api_secret_key` (the app's `client_secret`) is used to sign *every* webhook for *every* installed shop of that app, and the signature covers only the body, an attacker who controls one shop that has installed the app can capture a legitimately-signed webhook (body + HMAC) delivered to their own endpoint, then replay that exact `(raw_body, hmac)` pair while substituting the `x-shopify-shop-domain` (and/or `topic`/`webhook-id`) header to any value they choose. `Utils::HmacValidator.validate` will still succeed because it only checks the body against the HMAC, and `Registry.process` will invoke the app's handler with `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)` using the attacker-controlled `shop` value: [4](#0-3) 

Any application logic that uses `data.shop` to key which merchant's records to update/read (a common pattern, since this is the only shop-identifying field the gem hands the handler) can be tricked into attributing a webhook payload originating from shop A to shop B, i.e. a cross-tenant confusion enabled purely by gaps in what the gem signs versus what it trusts.

### Impact Explanation
This is a break of a tenant-binding equality that the gem is responsible for enforcing (the HMAC is the *only* authentication mechanism `Registry.process` performs), which maps to "cross-tenant access" — a Critical impact category per the scope rules. An attacker with a legitimate (even single, low-privilege) install of the target app can, without any additional secrets, forge webhook deliveries attributing arbitrary bodies to an arbitrary shop domain of their choosing, because the shop identity is taken from an unauthenticated header untouched by the signature.

### Likelihood Explanation
Likelihood is moderate-to-high in a realistic deployment: any attacker can install the app on their own shop (a normal, unprivileged action for a public app), which grants them a stream of validly-signed `(body, hmac)` pairs sent to their own endpoint. No secret, TLS interception, or privileged account is required — only ordinary use of the app as a merchant, then crafting a new HTTP request with the captured body/HMAC and a modified `shop` header pointed at the process() endpoint.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the signed material verified during webhook processing, or independently verify that `request.shop` corresponds to a shop with an active, expected session/install before trusting it in `WebhookMetadata`. At minimum, `to_signable_string` for `Webhooks::Request` should incorporate the `shop-domain` header (mirroring how Shopify's real HMAC verification for webhooks binds the full raw body plus needing per-shop context validation at the app layer), and the gem's documentation/API should make explicit that `WebhookMetadata#shop` is unauthenticated unless independently checked.

### Proof of Concept
1. Install the app on `attacker-shop.myshopify.com`; trigger any webhook topic so Shopify sends a legitimately-signed payload to the attacker's own registered endpoint. Capture `raw_body` and the `x-shopify-hmac-sha256` header value — both are valid under the shared `api_secret_key`.
2. Construct a new HTTP request to the victim app's webhook endpoint with the same `raw_body` and `x-shopify-hmac-sha256`, but set `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. Call:
```ruby
request = ShopifyAPI::Webhooks::Request.new(raw_body: captured_body, headers: {
  "x-shopify-topic" => captured_topic,
  "x-shopify-hmac-sha256" => captured_hmac,
  "x-shopify-shop-domain" => "victim-shop.myshopify.com",
})
ShopifyAPI::Webhooks::Registry.process(request)
```
4. `Utils::HmacValidator.validate(request)` returns `true` (it only checks `raw_body`), and the registered handler is invoked with `WebhookMetadata#shop == "victim-shop.myshopify.com"`, even though the payload was never sent by Shopify for that shop. [4](#0-3) [5](#0-4)

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

**File:** lib/shopify_api/webhooks/request.rb (L10-43)
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

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
      end
```
