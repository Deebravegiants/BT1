Confirms the finding: docs explicitly document that `Registry.process` "will verify the request did indeed come from Shopify" (line 125), implying the shop/topic/webhook_id identity is trusted as authenticated — but the HMAC in `HmacValidator.validate` only signs `to_signable_string`, which for webhooks is `@raw_body` alone [1](#0-0) . The `shop`, `topic`, `webhook_id`, and `api_version` fields are read directly from HTTP headers with no cryptographic binding to the signature [2](#0-1) , yet `Registry.process` forwards these unverified header values straight into `WebhookMetadata` passed to the app's handler [3](#0-2) .

### Title
Webhook `shop`/`topic`/`webhook_id` identity headers are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats an HMAC-valid webhook as fully authenticated ("verify the request did indeed come from Shopify"), but the HMAC only signs the raw request body. The `shop`, `topic`, `webhook_id`, and `api_version` values consumed by the app are taken unauthenticated from HTTP headers.

### Finding Description
`Utils::HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` and compares it against the received `hmac` [4](#0-3) . For webhooks, `Request#to_signable_string` returns only `@raw_body` [1](#0-0) . All the other identity fields — `shop`, `topic`, `webhook_id`, `api_version` — are parsed straight from attacker-controllable HTTP headers via `shopify_header`, with no signature coverage at all [2](#0-1) .

`Registry.process` only checks `Utils::HmacValidator.validate(request)` (i.e., body-only) before dispatching to the handler using `request.shop`, `request.topic`, and `request.webhook_id` straight from headers [3](#0-2) . There is no check binding the asserted `shop-domain`/`topic` header to the body content, and no per-shop secret is used — the app's single `client_secret` computes the same HMAC regardless of which shop or topic the body was originally issued for.

This is exactly the identity-binding gap the report's bug class targets: the value that downstream logic *acts on* (`shop` identity used to key sessions, jobs, and business logic in the handler) is not the value the HMAC actually *covers* (only the raw body bytes).

### Impact Explanation
Because the app's `client_secret` is shared across every shop that installs the app, any unprivileged actor who can install (or has installed) the app on their own shop receives legitimately HMAC-signed webhook requests for their own shop. That attacker can capture one such `(raw_body, hmac)` pair and replay it to the app's webhook endpoint while forging the `X-Shopify-Shop-Domain` / `shopify-shop-domain` header (and/or `topic`, `webhook-id`) to claim a different shop or topic. `HmacValidator.validate` still returns true because it only checks the untouched body against the shared secret, and `Registry.process` will dispatch to the handler with the attacker-chosen `shop` value in `WebhookMetadata#shop` [5](#0-4) . Since the documented handler pattern uses `data.shop` to key session lookups, job enqueueing, and per-tenant persistence [6](#0-5) , this enables cross-tenant data confusion/injection: an attacker can make the app record another shop's data under attacker-supplied content, or replay their own webhook body under a victim's identity, satisfying the "cross-tenant access" impact bar.

### Likelihood Explanation
Moderate: it requires the attacker to obtain at least one legitimately signed `(body, hmac)` pair, which any user of a multi-tenant app can trivially get by installing the app on their own store (an unprivileged action, no leaked credentials, no `api_secret_key` needed) and capturing their own inbound webhook traffic. No TLS interception or social engineering is required. The forged replay is a simple HTTP POST with modified headers, using the still-valid HMAC.

### Recommendation
Bind the shop/topic identity into the signature verification path instead of trusting bare headers: either (a) require the gem's `HmacValidator`/`Registry.process` to additionally cross-check the header-asserted `shop`/`topic` against a value embedded in or derivable from the signed body/context (e.g., verify against a known registered webhook `shop` for that `webhook_id`, or require the host app to look up and pin the expected shop before calling `process`), or (b) explicitly document and enforce that `Registry.process` callers MUST independently authenticate the `shop-domain` header (e.g. via a per-shop registration lookup) before trusting `WebhookMetadata#shop`, rather than describing HMAC validation as verifying that "the request did indeed come from Shopify" for all fields.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and receives a legitimate webhook, e.g. topic `orders/create`, body `B`, with header `X-Shopify-Hmac-Sha256: H` computed over `B` using the app's `client_secret`.
2. Attacker replays the exact same `raw_body: B` and `X-Shopify-Hmac-Sha256: H` to the app's webhook endpoint but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and/or a different `X-Shopify-Topic`).
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)` builds a request object; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only [1](#0-0)  and succeeds because `B` and `H` are unmodified.
4. `Registry.process` dispatches `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))` with `shop == "victim-shop.myshopify.com"` even though the body content actually originated from the attacker's own shop [3](#0-2) .
5. The host app's handler (per the documented pattern) processes/stores this attacker-controlled body under the victim shop's identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```
