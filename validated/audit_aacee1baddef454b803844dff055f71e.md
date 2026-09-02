Found it: in `ShopifyAPI::Webhooks::Request`, the HMAC (`Utils::HmacValidator.validate`) only signs `@raw_body` via `to_signable_string`, but `shop`, `topic`, `api_version`, and `webhook_id` are all read straight from unauthenticated HTTP headers (`shopify-shop-domain`, `shopify-topic`, etc.) and are never included in the signed bytes. Any caller/handler that trusts `request.shop` for tenant identification is trusting a value the HMAC never covers.

### Title
Webhook `shop`/`topic` headers are trusted for tenant identity but are not covered by the HMAC signature - (File: `lib/shopify_api/webhooks/registry.rb`, `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies the webhook's authenticity solely by validating the HMAC over the raw request body [1](#0-0) . But the identity fields handed to the app's handler — `shop`, `topic`, `api_version`, `webhook_id` — are read directly from HTTP headers and are never part of the signed bytes [2](#0-1) .

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body` [3](#0-2) . `Utils::HmacValidator.validate` computes `HMAC(secret, to_signable_string)` and compares it against `request.hmac`, which is itself derived from the `shopify-hmac-sha256` header [4](#0-3) [5](#0-4) . This proves the *body* was produced by someone holding the shared secret (Shopify) — but `shop`, `topic`, `api_version`, and `webhook_id` are read from separate headers (`shopify-shop-domain`, `shopify-topic`, `shopify-api-version`, `shopify-webhook-id`) that are outside that signed scope [6](#0-5) .

`Registry.process` passes these unauthenticated header values straight to the app's handler as the tenant/topic context after only checking the body HMAC: `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))` [1](#0-0) .

The binding that should hold is:
`shop header value == shop that produced/authorized the signed body`

but the gem only enforces:
`HMAC(secret, raw_body) == received_signature`

with no cryptographic tie between the signed body bytes and the `shop`/`topic` header values used downstream. This is the "field acted on but not covered by the HMAC" analog called out in scope: an attacker who can influence a webhook delivery pipeline (e.g., a reverse proxy, load balancer, queueing layer, or any component that forwards Shopify's raw body but lets header values be re-attached/modified before this gem processes them) can present a *body from shop A* labeled with `shopify-shop-domain: shop-B.myshopify.com`, and this gem will pass the app's handler a `WebhookMetadata` claiming the webhook is for shop B while the signature only proves the body byte content, not which shop/topic it belongs to.

### Impact Explanation
If the host app's webhook handler uses `WebhookMetadata#shop` (as this gem instructs it to) to select which merchant's data/tenant record the payload should be applied to, an attacker able to manipulate headers on the path into this gem (while the raw body + valid HMAC pass unchanged) can cause cross-tenant data to be attributed to, or written under, the wrong shop. This falls under the Critical "cross-tenant access" impact category, because the identity binding this gem is documented to guarantee (an authenticated Shopify webhook for shop X) is not actually cryptographically enforced for the `shop`/`topic` metadata it hands back.

### Likelihood Explanation
Exploitability depends on whether headers can be separated from/re-associated with the raw body somewhere between Shopify and this gem's `Webhooks::Request.new(raw_body:, headers:)` call (e.g., shared caching/proxy layers, header-rewriting middlewares, or any component that reconstructs headers independently of the body). This is a real architectural gap in the gem itself (it never binds shop/topic into the HMAC), even though many typical single-webhook-endpoint deployments may not expose an attacker-reachable path to desynchronize headers from body. Given the uncertainty about deployment topology, likelihood is moderate rather than certain.

### Recommendation
- Sign (or otherwise cryptographically bind) the `shop`, `topic`, and `webhook_id` header values together with the body before verification — e.g., include them in `to_signable_string`, or independently verify the `shop` value against the app's own record of the shop that owns the webhook subscription (`webhook_id`) before trusting it.
- At minimum, document that `WebhookMetadata#shop`/`#topic` are unauthenticated header echoes and instruct integrators to independently corroborate `shop` against their own tenant registry (e.g., an existing, previously-established session for that shop) rather than trusting the header value alone.

### Proof of Concept
Conceptual (library-level) PoC, since exploitation requires header/body desynchronization somewhere in the delivery path an app operator controls:
1. Attacker captures/replays a legitimately-signed webhook raw body+HMAC for `shop-a.myshopify.com` (or otherwise obtains any raw body + valid HMAC pair, e.g., via a shared endpoint that fans out to multiple header variants).
2. Attacker (or a compromised/misconfigured intermediary in the app's ingress stack) forwards the same `raw_body` and `hmac-sha256` header to the app's webhook endpoint, but sets `shopify-shop-domain: shop-b.myshopify.com` and/or a different `shopify-topic`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` builds a request object; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which validates using `to_signable_string` (`= raw_body`) only [7](#0-6) . Validation succeeds because the body/HMAC pair is untouched.
4. `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` is built from the attacker-controlled headers and handed to the app's handler as if it were an authenticated fact [8](#0-7) , even though nothing in the signature verification touched `shop` or `topic`.

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

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
```
