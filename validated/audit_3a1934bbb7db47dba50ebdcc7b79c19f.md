### Title
Webhook `shop-domain`, `topic`, and `webhook-id` headers are not covered by the HMAC, allowing cross-tenant header spoofing on replayed webhooks - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates only the raw request body via HMAC, then trusts the `shop-domain`, `topic`, `api-version`, and `webhook-id` headers verbatim to route the request and to populate `WebhookMetadata` passed to the app's handler. None of these headers are part of the signed content, so their values can be freely altered on a request that still carries a valid HMAC for the (unrelated) body.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` computes the HMAC exclusively over `to_signable_string`, i.e. the body bytes: [2](#0-1) 

Yet `Request#shop`, `Request#topic`, `Request#api_version`, and `Request#webhook_id` are all read directly from HTTP headers without any cryptographic binding to the signed body: [3](#0-2) 

`Registry.process` uses `request.topic` (unauthenticated) to select the handler, and forwards `request.shop`, `request.webhook_id`, `request.api_version` (all unauthenticated) straight into `WebhookMetadata`, which is the object the host application's business logic acts on: [4](#0-3) [5](#0-4) 

The broken binding, stated as an equality: the gem implicitly assumes
`HMAC-verified(body) == HMAC-verified(shop, topic, webhook_id, api_version)`,
but in reality only `HMAC-verified(body)` holds; `shop`, `topic`, `webhook_id`, and `api_version` are attacker-controllable metadata layered on top of a validly-signed body.

### Impact Explanation
This is the exact analog class called out in the rules — "a field acted on but not covered by the HMAC." An unprivileged internet user who is themselves a legitimate merchant/tenant of a multi-tenant app built on this gem can:
1. Trigger a real webhook from their own store (e.g. `orders/create`), which Shopify signs over the body only, using the app's real `api_secret_key` — a secret the attacker never needs to know.
2. Capture that valid `(raw_body, hmac)` pair (it's delivered to a public HTTP endpoint the attacker controls the triggering of; the body content is entirely attacker-chosen since it reflects data on their own store).
3. Replay the identical body/HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header for a victim tenant's domain, and/or substituting the `x-shopify-topic` header for a different topic (e.g. `app/uninstalled`, `shop/redact`).

Because `Registry.process` never validates that `shop` or `topic` are bound to the signed payload, the app's handler executes attacker-chosen body content while believing it originated from the victim tenant and/or a different event type. Depending on what the host app's handler does with `data.shop` and `data.body` (e.g. looking up the victim's stored session/access token and mutating data keyed by that shop, or triggering redaction/uninstall side effects), this crosses a tenant boundary using only a validly-signed webhook the attacker legitimately obtained for their own store — i.e., cross-tenant access enabled by a credential-binding gap in the gem.

### Likelihood Explanation
Moderate-to-high for apps that rely on `WebhookMetadata#shop` or `#topic` for authorization/dispatch decisions (a normal and encouraged usage pattern per this gem's documented `WebhookHandler` interface). No secrets, tokens, or privileged access are required — only the ability to install the app on one's own store (any internet user) and to send an HTTP POST to the app's public webhook endpoint with modified headers, which requires no interaction with Shopify's own infrastructure once a legitimate signed body/HMAC pair has been observed.

### Recommendation
Include `shop-domain`, `topic`, `api-version`, and `webhook-id` in the signed material verified by `HmacValidator` (e.g., construct `to_signable_string` from a canonical concatenation of these headers plus the body, mirroring how Shopify signs OAuth/App-Bridge payloads), or otherwise cryptographically bind these header values before they are exposed via `WebhookMetadata` to host-application handlers. At minimum, document prominently that `WebhookMetadata#shop`/`#topic`/`#webhook_id` are unauthenticated and must not be trusted for tenant-scoping decisions without independent verification.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and performs an action that Shopify will webhook for (e.g. creates an order), causing Shopify to POST a body `B` with header `x-shopify-hmac-sha256: HMAC(secret, B)` and `x-shopify-shop-domain: attacker.myshopify.com` to the app's public webhook endpoint.
2. Attacker captures `B` and the valid HMAC value (it is fully attacker-observable since the endpoint is public and the attacker triggered the event).
3. Attacker crafts a new POST to the same endpoint with the identical body `B` and identical `x-shopify-hmac-sha256` value, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` (and optionally changes `x-shopify-topic`).
4. `ShopifyAPI::Utils::HmacValidator.validate` returns `true` because it only checks `B` against the HMAC, per `lib/shopify_api/utils/hmac_validator.rb` lines 26-31.
5. `ShopifyAPI::Webhooks::Registry.process` (lib/shopify_api/webhooks/registry.rb lines 188-200) dispatches to the handler for the (possibly attacker-chosen) topic and constructs `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` even though that shop never sent this data — demonstrating the unauthenticated header is trusted downstream by design of the gem's public API.

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
