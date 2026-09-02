Confirmed. The `Registry.process` flow validates HMAC solely over the raw request body via `Utils::HmacValidator.validate(request)`, where `Request#to_signable_string` returns only `@raw_body`, but `Request#shop` and `Request#topic` are pulled from unauthenticated headers not covered by that signature.### Title
Webhook shop-tenant identity is not bound by the HMAC signature, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook by validating an HMAC computed only over the raw request body, but the tenant-identifying `shop` field (and `topic`) is read directly from an unauthenticated HTTP header and passed straight to the app's handler. This breaks the identity binding `shop authenticated == shop acted upon`, allowing a party who possesses a validly-signed webhook body (e.g., from their own store) to relabel it as belonging to a different shop.

### Finding Description
`Utils::HmacValidator.validate` computes and compares the signature only against `verifiable_query.to_signable_string`. [1](#0-0) 

For webhooks, `to_signable_string` returns solely the raw HTTP body — none of the HTTP headers, including `shopify-shop-domain`, `shopify-topic`, or `shopify-webhook-id`, are included in the signed material: [2](#0-1) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop` (and `request.topic`) — values sourced from headers — to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

`WebhookMetadata.shop` is a plain `String` field with no further verification: [4](#0-3) 

Because the HMAC only proves "this body was signed with the app's secret at some point for some topic/shop," and not "this body belongs to shop X," an entity that legitimately receives a signed webhook for their own store (a normal, unprivileged merchant using the same app) can replay that same raw body to the app's webhook endpoint while substituting the `shopify-shop-domain` (and/or `shopify-topic`) header for a different tenant. `HmacValidator.validate` will still pass because it only checks the body against the shared `api_secret_key`, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the data belongs to the victim shop.

The gem-level identity equality that should hold is:
`shop bound by signature == shop delivered to handler`
but in this code it is actually:
`shop bound by signature (body only) != shop delivered to handler (unauthenticated header)`.

### Impact Explanation
Any application built on this gem that uses `WebhookMetadata#shop` to select which tenant's data to update (the gem's documented and intended usage pattern shown in its own tests, e.g. `assert_equal(@shop, data.shop)`) is exposed to cross-tenant data injection: a merchant/attacker can cause their own webhook payload to be processed and stored under a different shop's identity, since the gem provides no cryptographic binding between the shop and the payload. This matches the "Critical – cross-tenant access" impact category, because the vulnerability originates entirely within this gem's own webhook verification code (`HmacValidator` + `Webhooks::Request`/`Registry`), not from the host application misusing an undocumented API. [5](#0-4) 

### Likelihood Explanation
Exploitation requires only: (1) being a merchant/user of an app built on this gem (no elevated privilege, no access to `api_secret_key`), (2) capturing one legitimately-signed webhook body sent to their own shop (trivial, since it is delivered to their own endpoint or can be triggered by ordinary store actions), and (3) resending it with a modified `shop-domain`/`topic` header to the same endpoint. No cryptography needs to be broken — the vulnerable code path (`HmacValidator.validate` + `Request#shop`) simply never binds the two together.

### Recommendation
Include the tenant-identifying headers (`shop-domain`, `topic`, `webhook-id`) in the HMAC-covered signable string for webhooks, or otherwise cryptographically bind them (e.g., derive an HMAC over `shop|topic|body` rather than `body` alone) in `Webhooks::Request#to_signable_string`/`hmac` and `Utils::HmacValidator`, so that a tampered `shop-domain` header invalidates the signature.

### Proof of Concept
1. App using this gem registers a webhook handler for topic `orders/create` and, per documented usage, keys tenant data off `data.shop`.
2. Attacker's own shop (`attacker-shop.myshopify.com`) receives a legitimate webhook POST to the app's endpoint:
   - Headers: `x-shopify-hmac-sha256: <valid HMAC of body>`, `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: orders/create`
   - Body: attacker-controlled JSON (order data is largely attacker-influenced content within their own store).
3. Attacker resends the identical body and HMAC header to the same app endpoint, only changing `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:26-31`) recomputes the HMAC over the unchanged body and it matches — validation succeeds.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) builds `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and invokes the app handler, which now processes attacker-supplied data as if it belongs to the victim tenant.

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
