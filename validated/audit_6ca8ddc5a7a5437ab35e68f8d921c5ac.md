Confirmed: `WebhookMetadata.shop` (from `Request#shop`, i.e. the `x-shopify-shop-domain` / `shopify-shop-domain` header) is handed to the app's `WebhookHandler#handle` while the HMAC only ever signs `@raw_body` [1](#0-0) , and `HmacValidator.validate` verifies exactly `verifiable_query.to_signable_string` against the header-supplied `hmac` [2](#0-1) , with no shop binding anywhere in that check.

### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as authentic for whatever shop is named in the `x-shopify-shop-domain` (or `shopify-shop-domain`) header, but that header is never included in the HMAC that is verified. The HMAC only covers the raw request body. This breaks the identity binding: `hmac_verified_bytes == raw_body` while `shop_used_for_processing == unauthenticated_header`.

### Finding Description
`Registry.process` validates a webhook solely via `Utils::HmacValidator.validate(request)`, then dispatches to the app handler with `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)` [3](#0-2) .

`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` and compares it to the `hmac` field using `OpenSSL.secure_compare` [4](#0-3) .

For `Webhooks::Request`, `to_signable_string` returns only `@raw_body`; `hmac` is decoded from the `hmac-sha256` header, and `shop` is read from a completely separate, unsigned header (`shop-domain`) [5](#0-4) .

Because the HMAC never binds `shop` to the body, any request whose body byte-for-byte matches a body that was legitimately signed by Shopify for shop A (e.g. an attacker's own test/development store, which they fully control and can trigger webhooks for) will still pass HMAC validation even if the `shop-domain` header is changed to shop B. The `shop` value handed to the app's `WebhookHandler#handle` (`WebhookMetadata#shop` [6](#0-5) ) is thus attacker-controlled and unauthenticated, even though the gem asserts the whole request "did indeed come from Shopify" [7](#0-6) .

This is directly analogous to the reported bug class: a field acted upon by downstream logic (the `shop` used to attribute/process the webhook) is not covered by the authentication mechanism (HMAC over body only).

### Impact Explanation
Applications built on top of `ShopifyAPI::Webhooks::Registry.process` reasonably assume that once HMAC validation succeeds, every field of the verified webhook — including `shop` — is authentic and safe to use as a tenant identifier (e.g., to look up a session/access token, write data, or trigger side effects scoped "per shop"). Since `shop` is not bound to the signature, an attacker who controls one Shopify store (a normal, unprivileged merchant account) can register webhooks on their own store, capture the legitimately-signed request body/HMAC pair, and replay it against the app's webhook endpoint with the `shop-domain` header rewritten to a victim shop. This enables cross-tenant confusion: the app processes data/events attributed to a shop the attacker does not own, potentially causing cross-tenant state corruption depending on how the host app keys per-shop side effects off `WebhookMetadata#shop`.

### Likelihood Explanation
The attacker only needs their own legitimate Shopify store (not privileged access to the target) to obtain one validly-signed webhook body/HMAC pair — no access to `api_secret_key`, tokens, or the app's other credentials. The attack surface is directly reachable via the gem's public `Registry.process` API as documented and used by all integrating apps.

### Recommendation
Extend `Webhooks::Request#to_signable_string` (or `HmacValidator`) to incorporate the `shop-domain` (and ideally `topic`) header into the signed material, or otherwise cryptographically bind the shop value to the HMAC before trusting `request.shop` in `WebhookMetadata`.

### Proof of Concept
1. Attacker owns/operates `attacker-shop.myshopify.com` and registers a webhook (e.g., `orders/create`) for it.
2. Attacker triggers the webhook on their own shop, capturing the raw body and the legitimately Shopify-computed `x-shopify-hmac-sha256` header value for that body.
3. Attacker sends a request to the target app's webhook endpoint with the same raw body and HMAC header, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `raw_body` against the HMAC — validation succeeds [8](#0-7) .
5. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"`, even though Shopify never sent this webhook for that shop [9](#0-8) .

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

**File:** docs/usage/webhooks.md (L123-125)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
