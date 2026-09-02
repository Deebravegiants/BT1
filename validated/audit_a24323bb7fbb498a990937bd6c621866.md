### Title
Webhook shop/topic/webhook-id identity is trusted from unauthenticated HTTP headers while only the raw body is HMAC-covered — ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` but defines `to_signable_string` to return only the raw request body: [1](#0-0) 

Meanwhile, `shop`, `topic`, and `webhook_id` — the fields used to route and attribute the webhook to a tenant — are read directly from HTTP headers that are never included in the signed content: [2](#0-1) 

`Registry.process` validates only the body's HMAC before dispatching the handler with `request.shop` used as the tenant identity for the webhook payload: [3](#0-2) 

### Finding Description
The binding that should hold is: `shop asserted in HMAC-signed bytes == shop the handler acts on`. Here it does not — `HmacValidator.validate(request)` only proves that the *body bytes* were signed with the app's `api_secret_key`; it says nothing about which shop/topic/webhook-id header accompanied those bytes. Since `to_signable_string` for `Webhooks::Request` returns solely `@raw_body`, the `X-Shopify-Shop-Domain`, `X-Shopify-Topic`, and `X-Shopify-Webhook-Id` headers are parsed and trusted (`request.shop`, `request.topic`, `request.webhook_id`) without being part of what the HMAC actually authenticates.

Because HMAC-SHA256 over a fixed body can be valid for that body no matter which headers are sent alongside it, an entity that possesses one legitimately-signed body+HMAC pair (e.g., a merchant/store owner who has installed the app and can observe genuine webhook deliveries addressed to their own shop) can resend that same body/HMAC to the app's webhook endpoint with a different `shop-domain` header value. `Utils::HmacValidator.validate` will report the HMAC as valid (it re-verifies against `raw_body` alone), and `Registry.process` will hand off `WebhookMetadata` tagged with the attacker-chosen `shop`, `topic`, and `webhook_id` to the app's handler: [4](#0-3) 

This is the "field acted on but not covered by the HMAC" bug class from the rules — analogous to the GitLab CI cache report, where an attacker-controlled, unauthenticated value (`shop-domain` header here, cache `key` there) determines which tenant's resource is written to/read from, while the layer meant to authenticate the request only covers a different, narrower scope (raw body vs. cache key).

### Impact Explanation
If a host application relies on `request.shop` from this gem's `Webhooks::Request`/`Registry` as the trusted tenant identifier (which is the documented intended use — see `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)`), an attacker who controls one shop's webhook deliveries can inject data attributed to a different shop into the host app's per-tenant processing pipeline. This is a cross-tenant data poisoning primitive: the app will believe body data (e.g., product update, order, GDPR payload) originated from shop B, when it was actually a replay of shop A's payload. Depending on the handler, this could corrupt another merchant's records, trigger unauthorized actions scoped to shop B, or leak shop A's data into shop B's context.

### Likelihood Explanation
Exploitation requires only: (1) the attacker be a genuine, unprivileged app-installing merchant capable of receiving real webhook deliveries for their own shop (no `api_secret_key`, access token, or privileged access needed), and (2) network access to the app's public webhook endpoint to replay the captured body/HMAC with a forged `shop-domain`/`topic`/`webhook-id` header. Because the vulnerable check lives entirely inside this gem's `Webhooks::Request`/`HmacValidator`/`Registry` code path and is the documented way to consume webhooks, no misuse of the gem's documented API is required.

### Recommendation
Include `shop`, `topic`, and `webhook_id` (and ideally a timestamp/nonce) in the signable content used for HMAC verification, or independently bind/verify these header values against the shop context the app expects for that endpoint before dispatching to handlers. At minimum, `to_signable_string` should not silently narrow the signed surface to only the raw body when other fields drive tenant-sensitive routing.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers a webhook (e.g., `products/update`), capturing the raw POST body `B` and its `X-Shopify-Hmac-Sha256` header `H` — both are legitimately produced by Shopify using the app's real `client_secret`.
2. Attacker resends an HTTP POST to the app's webhook endpoint with the same body `B` and header `H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` and/or a different `X-Shopify-Topic`.
3. `Webhooks::Request.new` builds a request object where `hmac` decodes `H` and `to_signable_string` returns `B` — matching the original signature since headers are excluded from the signable string: [5](#0-4) 
4. `Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `B` against `H`: [6](#0-5) 
5. The handler is invoked with `shop: request.shop` set to `victim-shop.myshopify.com` and body `B` from the attacker's own shop — a cross-tenant data-poisoning webhook delivery accepted as authentic by the app.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
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
