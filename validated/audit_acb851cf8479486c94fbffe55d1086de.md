## Title
Webhook `shop-domain` header is not covered by HMAC verification, allowing cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body via `Utils::HmacValidator.validate(request)`. However, `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, while the shop identity attached to the event (`request.shop`) is read directly from the unauthenticated `x-shopify-shop-domain` / `shopify-shop-domain` header. The HMAC signature therefore binds only the JSON body bytes, never the shop-domain header, breaking the equality: `shop authenticated by HMAC == shop attributed to the processed event`.

### Finding Description
`Registry.process` computes trust for an incoming webhook exclusively from: [1](#0-0) 

`Utils::HmacValidator.validate` recomputes the HMAC using `verifiable_query.to_signable_string` and compares it against `verifiable_query.hmac`: [2](#0-1) 

For `ShopifyAPI::Webhooks::Request`, `to_signable_string` returns **only** the raw body, and `hmac`/`shop` are both independently parsed from HTTP headers: [3](#0-2) 

Since only `@raw_body` is signed, the `shop-domain` header can be modified without invalidating the HMAC (which is computed purely over the JSON body using the app's shared `api_secret_key`). `Registry.process` passes this unauthenticated `request.shop` value straight to the app's handler as the tenant identifier for the event: [1](#0-0) 

Contrast this with the OAuth callback flow, where `shop` **is** included in the HMAC-signed payload: [4](#0-3) 

This confirms the webhook path is the outlier: the field acted on (`shop`, used to key application data/session lookups per the documented handler contract) is not covered by the same signature that is treated as proof of authenticity.

### Impact Explanation
An unprivileged internet user who legitimately controls their own Shopify development/test store can install the target app and receive genuine, correctly-HMAC-signed webhooks for their own shop (e.g. `app/uninstalled`, `customers/data_request`, `orders/create`, etc.). Because the signature covers only the body, the attacker can replay that exact signed body while substituting the `x-shopify-shop-domain` header with an arbitrary victim shop domain. `Registry.process` will accept the forged request as authentic (HMAC still validates) and dispatch it to the handler tagged with the victim's shop. Depending on what the host app's handler does with `data.shop` (e.g., delete/rotate the victim's stored access token on a forged `app/uninstalled`, trigger GDPR data deletion for the victim's customers, or write attacker-controlled body content under the victim's tenant), this results in cross-tenant impact — the exact category called out as Critical in scope.

### Likelihood Explanation
Any user capable of creating/controlling a Shopify shop where the target app is installed can trivially capture one legitimate webhook delivery (readily observable, e.g. via a webhook proxy/inspector) and replay it with a modified header — no access to `api_secret_key`, tokens, or privileged accounts is required. This is a straightforward, repeatable HTTP-level forgery once one legitimate webhook has been observed.

### Recommendation
Bind the shop identity (and other trust-relevant headers such as `topic`, `webhook-id`, `api-version`) into the HMAC-signed payload verification, e.g., by including the relevant header values in `to_signable_string`, or by independently verifying shop identity through a source that is itself authenticated (such as looking up the session by the `shop` and confirming this shop is associated with the currently validated webhook subscription/topic), rather than trusting a header that sits outside the cryptographic envelope.

### Proof of Concept
1. Register the app for webhooks and control shop `attacker.myshopify.com`, receiving a legitimate webhook (e.g., `orders/create`) with headers:
   - `x-shopify-hmac-sha256: <valid signature over body B>`
   - `x-shopify-shop-domain: attacker.myshopify.com`
   - body `B`
2. Replay the same request to the app's webhook endpoint, keeping `x-shopify-hmac-sha256` and body `B` unchanged, but set `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Utils::HmacValidator.validate(request)` in `Registry.process` still succeeds because it only checks `raw_body` against the signature; `request.shop` now reports `victim.myshopify.com`, and the handler processes attacker-controlled data as if it originated from the victim's shop.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
