Confirmed: `WebhookMetadata.shop` (and `topic`, `webhook_id`, `api_version`) are passed directly to the host app's handler, and these values come from unauthenticated headers, while `Utils::HmacValidator.validate` only verifies the raw request body against the shared `Context.api_secret_key`. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

### Title
Webhook `shop` identity is not bound by HMAC verification, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` (and `topic`, `webhook_id`, `api_version`) values solely from HTTP headers, which are never covered by the HMAC signature check. `Utils::HmacValidator.validate` only verifies `to_signable_string`, which is hard-coded to `@raw_body`. `Registry.process` treats HMAC success as full authentication of the request, then hands the attacker-controlled `shop` value straight to the host app's `WebhookHandler#handle` via `WebhookMetadata`, breaking the intended equality of "shop that produced the signed payload" == "shop attributed to the event."

### Finding Description
`Request#hmac`/`Request#to_signable_string` only ever sign/verify the raw JSON body: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all read from headers (`shopify-shop-domain`, `shopify-topic`, etc.) that are entirely attacker-controlled at the HTTP layer and are not part of the signed material: [5](#0-4) 

`HmacValidator.validate` computes the signature only over `verifiable_query.to_signable_string` (the body) using the app-wide `Context.api_secret_key`/`old_api_secret_key`, a secret shared across *every* shop that installs the app — it does not incorporate `shop` at all: [3](#0-2) 

`Registry.process` uses that same HMAC result to authorize dispatch, then forwards the unauthenticated `request.shop` value into `WebhookMetadata`, which is delivered to the host application's handler as the shop of record for the event: [6](#0-5) [4](#0-3) 

Because the same `client_secret` is used to sign webhooks for *all* shops that have installed the app, and only the raw body is bound by the signature, an unprivileged internet user who legitimately installs the app on their own (attacker-controlled) test shop can capture one valid `(raw_body, hmac)` pair from a webhook Shopify sends to their app, then replay that identical body/HMAC pair to the app's webhook endpoint while substituting an arbitrary victim `shop-domain` header. `Utils::HmacValidator.validate` will still succeed (it never inspected `shop`), and `Registry.process` will hand the forged `shop` value straight to the host app's handler as if the event genuinely originated from the victim tenant.

This breaks the equality: `shop authenticated by HMAC` == `shop attributed to the processed event`. The gem authenticates only "this body was signed by some installation of this app," not "this body was sent for *this* shop," yet the API surface (`WebhookMetadata#shop`) presents `shop` as trustworthy to the host application.

### Impact Explanation
This is a cross-tenant data-integrity/confusion vulnerability: a host application relying on `WebhookMetadata#shop` to look up per-tenant records (e.g., to update order/customer data, trigger redaction for GDPR `customers/redact`/`shop/redact`, or select a per-shop session/access token) can be made to act on a victim shop's identity using attacker-supplied body content, or conversely process a captured payload from one tenant under another tenant's identifier. Since apps commonly key their session/data store by `shop`, this can lead to cross-tenant state corruption using only unprivileged access (installing the app once as an attacker) — matching the report's "identity binding broken" theme (shop authenticated vs. shop used as processing key).

### Likelihood Explanation
Requires an attacker to install the target app on a shop they control (an unprivileged action available to anyone) and to be able to reach the app's public webhook endpoint. No `api_secret_key`, access token, or victim credentials are needed — only a captured legitimate `(body, hmac)` pair from the attacker's own installation and knowledge/guessing of a victim `myshopify.com` domain.

### Recommendation
Include `shop` (and ideally `topic`/`webhook_id`) in the signed material, or otherwise cryptographically bind the claimed `shop` header to the specific installation/session before dispatching to `WebhookHandler#handle`, so that `Registry.process` cannot be tricked into attributing a validly-signed body to an arbitrary shop.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` and captures a legitimate webhook request Shopify sends to the app's endpoint, noting the raw body and the `shopify-hmac-sha256` header value.
2. Attacker replays an HTTP POST to the app's webhook route with the identical raw body and `shopify-hmac-sha256` header, but sets `shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged request; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks the body against the app's shared secret [7](#0-6) .
4. `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))` is invoked with `shop == "victim-shop.myshopify.com"`, even though the body was never actually associated with that shop by Shopify [8](#0-7) .

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
