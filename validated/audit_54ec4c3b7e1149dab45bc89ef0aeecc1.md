This confirms the vulnerability: the documented API explicitly tells developers to trust `data.shop` (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)` per [1](#0-0) ), while the underlying `shop` value is never covered by the HMAC signature.

### Title
Webhook shop/topic identity spoofing via unsigned headers - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by validating an HMAC over the raw request body, but the `shop` and `topic` values that are handed to the app's handler (and that the gem's own documentation tells developers to trust for per-tenant routing/storage) are read directly from unauthenticated HTTP headers that are never included in the signed content.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body` [2](#0-1) , and `HmacValidator.validate_signature` computes/verifies the signature against that signable string alone [3](#0-2) . Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all parsed straight from HTTP headers (`shopify-shop-domain`, `shopify-topic`, etc.) with no cryptographic binding to those header values [4](#0-3) .

`Registry.process` validates only the HMAC of the body, then immediately trusts `request.topic` for handler dispatch and `request.shop` for the identity passed to the handler [5](#0-4) . This breaks the intended identity binding: "bytes verified" (the raw body, keyed by `api_secret_key`) versus "bytes parsed" (the `shop`/`topic` headers used for tenant attribution) are two different, unrelated data sources.

The gem's own documentation instructs integrators to key per-shop background work directly off `data.shop`: `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)` [1](#0-0) , and `WebhookMetadata` is a plain struct carrying `shop` as an authoritative field with no further verification performed by the gem [6](#0-5) .

### Impact Explanation
Any actor who can obtain one legitimately-signed webhook body/HMAC pair for the shared app secret (e.g., a merchant who has installed the app and receives their own genuine webhooks) can replay that exact body+HMAC to the app's public webhook endpoint while substituting the `shopify-shop-domain` (and/or `shopify-topic`) header for an arbitrary victim shop. `HmacValidator.validate` will still pass because it never inspects the headers, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the forged shop's identity together with the attacker-supplied body. Applications that follow the gem's documented pattern of using `data.shop` to attribute or persist webhook data will write/act on that body under the wrong tenant, resulting in cross-tenant data injection/corruption.

### Likelihood Explanation
Exploitation requires only network access to the app's public webhook URL and possession of one valid signed body for the target app's secret — attainable by any merchant who installs the app (a low-privilege, "unprivileged internet user" relative to other tenants). No access to `api_secret_key`, tokens, or the target shop's credentials is needed.

### Recommendation
Bind `shop` and `topic` (and any other routing-relevant header) into the HMAC-signed content, or otherwise cryptographically authenticate them (e.g., by including them in `to_signable_string`, or by having `Registry.process`/`WebhookMetadata` re-derive the shop from a value that is itself covered by the signature) so that the identity used for handler dispatch/attribution cannot diverge from the identity actually authenticated by `api_secret_key`.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and receives a real webhook, e.g. body `{"id":1}` with header `X-Shopify-Hmac-Sha256: <valid-hmac-of-body>` and `X-Shopify-Shop-Domain: attacker.myshopify.com`.
2. Attacker POSTs the identical raw body and HMAC header to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com` (and optionally a different `X-Shopify-Topic`).
3. `ShopifyAPI::Webhooks::Request.new` parses headers as-is; `Utils::HmacValidator.validate` recomputes the HMAC over `{"id":1}` using the shared `api_secret_key` and it matches, since the header changes don't affect `to_signable_string`.
4. `Registry.process` calls the app's handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: {"id":1}, ...)` [7](#0-6) .
5. If the host app follows the documented pattern of persisting/acting on `data.body` keyed by `data.shop` [1](#0-0) , attacker-controlled data is now written into `victim.myshopify.com`'s tenant context.

### Citations

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```

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
