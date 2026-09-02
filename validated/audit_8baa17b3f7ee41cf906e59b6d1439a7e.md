I have enough evidence to finalize the analysis.

### Title
Webhook `shop` identity is trusted from an unauthenticated header while the HMAC only covers the raw body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives `shop`, `topic`, `webhook_id`, and `api_version` directly from HTTP headers, but its HMAC signable string (`to_signable_string`) is defined as only the raw request body. `ShopifyAPI::Webhooks::Registry.process` verifies the HMAC and then unconditionally trusts `request.shop` when constructing `WebhookMetadata`, breaking the binding between "the body Shopify actually signed" and "the shop the app attributes that body to."

### Finding Description
`ShopifyAPI::Utils::HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` and compares it with the `hmac` header value [1](#0-0) . For webhooks, `to_signable_string` returns only `@raw_body`, not the shop-domain, topic, or webhook-id headers [2](#0-1) . Those identifying fields (`shop`, `topic`, `webhook_id`, `api_version`) are read straight from caller-supplied headers with no cryptographic linkage to the signed body [3](#0-2) .

`Registry.process` validates only the HMAC, then immediately hands `request.shop` (and `request.topic`, `request.webhook_id`) to the handler as the trusted tenant identity for the payload: `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...))` [4](#0-3) . Since the HMAC proves only "this body was produced with `api_secret_key`," not "this body belongs to this shop," an attacker who can obtain one valid (body, hmac) pair from Shopify — trivially available since anyone can install a free/dev app on their own store and receive real webhooks for it — can replay that exact body+HMAC to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` (and/or topic) header. The HMAC check still passes because it never looked at those headers, so `WebhookMetadata#shop` reports whatever domain the attacker chose, not the shop that actually owns the signed body.

The gem's own documentation reinforces that developers are expected to treat a passing `Registry.process` call as full authentication of the request's origin/identity: "This will verify the request did indeed come from Shopify and then call the specified handler for that webhook" [5](#0-4) , and the documented handler contract exposes `data.shop` as an authenticated field to key application logic on: `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)` [6](#0-5) . This is exactly the "shop authenticated vs. shop acted upon" split: the equality that should hold — `shop_bound_by_HMAC == shop_used_by_handler` — does not, because `shop` is outside the HMAC-covered signable string entirely.

### Impact Explanation
Any application built strictly on this gem's documented contract (using `data.shop` from a `Registry.process`-validated request as the authenticated tenant key) can be made to process data under an attacker-chosen shop identity, using a body/HMAC pair the attacker legitimately obtained for their own store. This is cross-tenant identity confusion delivered through a request that passes the gem's stated verification step, matching the "cross-tenant access" impact class.

### Likelihood Explanation
Exploitation requires only: (1) an attacker-controlled Shopify store (free/dev stores are trivially obtainable) subscribed to the same webhook topic the target app also handles, to legitimately harvest a valid (raw_body, hmac) pair, and (2) sending a forged HTTP POST to the victim app's public webhook endpoint with that body/HMAC and a spoofed `shop-domain` header. No access token, `client_secret`, or privileged account of the victim is needed.

### Recommendation
Include the shop domain (and ideally topic and webhook id) in the HMAC-covered signable string for webhook requests, or otherwise cryptographically bind them to the verified body, so `Registry.process`/`HmacValidator.validate` cannot pass for a body whose headers have been swapped to a different shop. At minimum, update documentation to clarify that `data.shop`/`data.topic` are not covered by HMAC verification and must not be treated as authenticated tenant identifiers without additional server-side cross-checks (e.g., confirming the shop has an active, matching webhook subscription/session).

### Proof of Concept
1. Attacker installs a (free/dev) app on their own store `attacker.myshopify.com` and subscribes to a webhook topic the target app also handles (e.g. `orders/create`).
2. Shopify sends a legitimate webhook to attacker's endpoint with body `B` and header `X-Shopify-Hmac-Sha256: H` where `H = HMAC-SHA256(secret, B)` and `X-Shopify-Shop-Domain: attacker.myshopify.com`.
3. Attacker captures `(B, H)` and POSTs to the victim app's webhook endpoint with the same body `B` and hmac header `H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and matching topic/webhook-id headers as desired).
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)` builds successfully; `Utils::HmacValidator.validate` recomputes HMAC over `B` only [7](#0-6)  and it matches `H`, so `Registry.process` proceeds and calls the app's handler with `data.shop == "victim-shop.myshopify.com"` [4](#0-3)  even though the body actually originated from the attacker's own store.

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

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
