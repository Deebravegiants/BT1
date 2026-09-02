### Title
Webhook `shop` and `topic` attribution is trusted from unauthenticated HTTP headers, not the HMAC-covered bytes - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by HMAC-validating the raw request body, but the `shop`, `topic`, `webhook_id`, and `api_version` values that are handed to the host application's handler as the tenant/identity context come from HTTP headers that are never included in the HMAC-signed bytes.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) . `Utils::HmacValidator.validate` computes the HMAC exclusively over `verifiable_query.to_signable_string` and compares it to the `hmac` field: [2](#0-1) . Meanwhile `Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are all read straight from HTTP headers (`shopify-shop-domain`, `shopify-topic`, etc.) with no cross-check against the body: [3](#0-2) .

`Registry.process` then calls the handler with `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)` after only checking `Utils::HmacValidator.validate(request)`: [4](#0-3)  and [5](#0-4) .

This breaks the intended identity binding `shop authenticated == shop attributed to the webhook`. Since only the raw body is HMAC-covered, an attacker can take a legitimate, validly-signed webhook payload (e.g., one delivered to their own Shopify store, which any unprivileged internet user can obtain by installing any app and receiving real Shopify webhooks) and replay it to a merchant app's webhook endpoint while substituting the `X-Shopify-Shop-Domain`, `X-Shopify-Topic`, `X-Shopify-Webhook-Id`, or `X-Shopify-Api-Version` headers. The HMAC validation still succeeds because it only checks that the body bytes match the signature — it never verifies the headers are consistent with what Shopify actually sent for that shop/topic.

### Impact Explanation
Any handler that uses `WebhookMetadata#shop` to look up or write per-tenant data (the documented/expected usage pattern — matching the shop field against the app's session/tenant store) can be tricked into associating attacker-supplied body content with a victim shop's identity, or associating a victim's legitimate signed data with the wrong topic/interpretation. This is a cross-tenant identity-binding break: the HMAC proves the body came from *some* Shopify-signed webhook, but not that it came from the specific shop or topic recorded in the (unauthenticated) headers used to route/attribute it.

### Likelihood Explanation
Exploitation requires only a valid HMAC-signed webhook body, obtainable by any unprivileged party who runs their own Shopify store (or captures any legitimate webhook delivery) — no `api_secret_key`, access token, or privileged account is needed. The attacker only needs network access to the merchant app's public webhook endpoint. This is a realistic, credential-free replay attack against a documented, commonly-used API surface (`Registry.process`).

### Recommendation
Include the identity-critical headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the HMAC-signable string, or otherwise cryptographically bind them to the body (e.g., verify the shop domain embedded in the JSON payload matches the header before trusting it), so that `Registry.process` cannot attribute a validly-signed body to an attacker-controlled shop/topic.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and receives a real webhook, e.g. `orders/create`, with a valid `X-Shopify-Hmac-Sha256` computed over the JSON body using the app's shared secret.
2. Attacker resends the identical raw body and HMAC header to the merchant app's public webhook endpoint, but changes `X-Shopify-Shop-Domain` to `victim.myshopify.com` (and optionally `X-Shopify-Topic`/`X-Shopify-Webhook-Id`).
3. `ShopifyAPI::Webhooks::Request.new` parses these headers unmodified (`lib/shopify_api/webhooks/request.rb:15-33`), and `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only re-computes the HMAC over `@raw_body` (`lib/shopify_api/webhooks/request.rb:35-38`, `lib/shopify_api/utils/hmac_validator.rb:26-31`) — validation succeeds because the body is unchanged.
4. The handler receives `WebhookMetadata(shop: "victim.myshopify.com", topic: ..., body: <attacker's data>)` and, if it uses `shop` to look up state/session for `victim.myshopify.com`, processes attacker-controlled content under the victim tenant's identity.

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
