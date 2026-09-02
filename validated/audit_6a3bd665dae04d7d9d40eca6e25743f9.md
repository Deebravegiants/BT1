## Title
Webhook shop attribution can be forged despite HMAC validation, enabling cross-tenant webhook spoofing - (`lib/shopify_api/webhooks/registry.rb`, `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as authenticated for a given shop once `Utils::HmacValidator.validate(request)` succeeds, and forwards `request.shop` (derived purely from the unsigned `X-Shopify-Shop-Domain` header) to the app's handler as trusted `WebhookMetadata.shop`. The HMAC, however, is computed only over the raw request body — it never binds the `shop`, `topic`, or `webhook-id` headers to the signature. This breaks the intended identity binding: `shop_header == shop_that_produced(hmac)`.

### Finding Description
`Utils::HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string`: [1](#0-0) 

For webhooks, `Request#to_signable_string` returns only the raw body: [2](#0-1) 

But `shop`, `topic`, `api_version`, and `webhook_id` are all read straight from HTTP headers, which are not part of the signable content at all: [3](#0-2) 

`Registry.process` validates only the HMAC, then unconditionally builds `WebhookMetadata` from `request.shop`/`request.topic`/etc. and dispatches it to the handler as if it were authenticated for that shop: [4](#0-3) 

Because `shop` (and `topic`/`webhook_id`) are outside the HMAC's coverage, any party who can produce one valid `(raw_body, hmac)` pair for the configured `api_secret_key` — for example a merchant who installs the app on their own store and captures one of their own legitimate webhook deliveries — can replay that exact `raw_body`/`hmac` pair to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header (e.g., a victim's shop domain) and/or `topic`/`webhook-id`. `Utils::HmacValidator.validate` will still return `true` because it only recomputes the signature over the untouched body, and `Registry.process` will hand the forged shop/topic to the handler as trusted metadata.

Equality that should hold but doesn't: `shop_header_used_by_handler == shop_that_actually_generated(hmac, raw_body)`. After the forged replay: LHS = victim shop, RHS = attacker's own shop — the binding is broken.

### Impact Explanation
An app author using this gem's `Webhooks::Registry.process` reasonably treats `WebhookMetadata#shop` as authenticated (it passed HMAC validation), because the gem's API gives no indication that `shop` is unsigned. A malicious but unprivileged actor who has valid HMAC material (trivially obtainable by installing the app on their own store) can attribute attacker-controlled webhook payloads to a different, victim shop domain. Depending on how the host app uses `data.shop` (e.g., to route the payload to shop-specific records, trigger shop-scoped side effects, or select credentials/session by shop), this enables cross-tenant data injection/corruption — a cross-tenant access scenario.

### Likelihood Explanation
Any actor able to install the app on at least one Shopify store (a normal, low-privilege action, including free development stores) can capture one legitimate `(body, hmac)` pair from their own webhook deliveries and replay it against the app's public webhook endpoint with a spoofed `shop-domain`/`topic` header. No access token, `client_secret`, or privileged access is required — this is directly reachable from the public internet by anyone who can install the app.

### Recommendation
Bind `shop`, `topic`, and `webhook_id` into the value verified against the HMAC (or independently cross-check the header-derived shop against a value embedded in the verified payload/subscription record) before constructing `WebhookMetadata` and dispatching to the handler in `Registry.process`. At minimum, document clearly that `WebhookMetadata#shop`/`#topic` are not covered by the signature so host apps cannot mistakenly treat them as authenticated.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and receives a legitimate webhook: raw body `B`, valid `X-Shopify-Hmac-Sha256: H` (computed with the app's real `api_secret_key`, which the attacker never sees).
2. Attacker replays an HTTP POST to the app's webhook endpoint with the same body `B` and header `H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)` → `true` (body/HMAC pair is untouched and valid). [5](#0-4) 
4. The handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` with attacker-controlled body content, even though the app never received an authentic webhook from that shop.

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
