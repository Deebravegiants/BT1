## Title
Webhook `shop-domain`, `topic`, and `webhook_id` headers are trusted without HMAC coverage, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` exposes `shop`, `topic`, `webhook_id`, and `api_version` as plain HTTP header reads, but the HMAC signature that `ShopifyAPI::Webhooks::Registry.process` validates only covers the raw request body, not these headers. Because Shopify apps sign webhooks with a single shared `client_secret` across every installed shop, any merchant who has installed the app can capture one of their own legitimately-signed webhook deliveries and replay it to the app's webhook endpoint with a forged `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) header. The HMAC check still passes because it never inspects those headers, so the app's handler receives attacker-controlled tenant identity attached to a validly-signed payload.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all read directly from attacker-controllable HTTP headers with no cryptographic binding: [2](#0-1) 

`HmacValidator.validate_signature` computes and compares the HMAC solely over `verifiable_query.to_signable_string`, i.e. the raw body only: [3](#0-2) 

`Registry.process` trusts `request.shop` (and `request.topic`, `request.webhook_id`) unconditionally once the body-only HMAC check passes, and forwards them straight into the handler's `WebhookMetadata`: [4](#0-3) 

This breaks the intended identity binding: `hmac-signed(body)` == `attacker-controlled(shop, topic, webhook_id)`. The equality that should hold — "the shop whose credentials produced this signature" equals "the shop the app attributes the payload to" — does not, since the signing secret (`client_secret`) is shared across all shops that installed the app, not shop-specific. Any installed merchant can therefore generate a validly-signed body (their own real webhook) and relabel it as belonging to a different shop.

### Impact Explanation
This is a cross-tenant confusion: the app processes a payload while believing it originates from a different shop than the one that actually produced/signed it. Depending on how the host app uses `WebhookMetadata#shop` (e.g., looking up which tenant's records to update, or fulfilling GDPR-mandatory `shop/redact`/`customers/redact`/`customers/data_request` topics), an attacker-controlled merchant can cause the app to attribute or act on data under an arbitrary target shop's identity, without ever needing that target's access token or credentials. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Any developer/merchant who installs the app is, by design, capable of receiving genuine webhook deliveries (valid HMAC) for their own shop. Forging the `shop-domain`/`topic`/`webhook-id` headers on replay requires no secret knowledge, only the ability to POST to the app's public webhook endpoint with modified headers — something explicitly reachable by any unprivileged internet user who has installed the app once. This is a low-effort, high-confidence exploitation path intrinsic to how `Request`/`Registry.process` are implemented in this gem.

### Recommendation
Bind the shop/topic/webhook identity into the signed material, or otherwise verify it independently of the header value:
- Include `shop`, `topic`, and `webhook_id` in the HMAC-signed string (`to_signable_string`) rather than only the raw body, if compatible with Shopify's webhook signing scheme, or
- Cross-check `request.shop` against a list of shops your app has valid sessions/installations for before acting on the payload, and
- Treat `topic`/`webhook_id` as identifiers to be revalidated against the registered handler/topic mapping (deduping by `webhook_id` alone is not sufficient authentication).

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and configures a webhook subscription (e.g. `orders/create`).
2. Shopify delivers a webhook to the app's endpoint with a valid `X-Shopify-Hmac-Sha256` computed via `OpenSSL::HMAC.hexdigest(sha256, client_secret, raw_body)` and header `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
3. Attacker captures `raw_body` and the valid HMAC header, then re-POSTs the exact same body/HMAC to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` parses `shop` as `victim-shop.myshopify.com` from the header.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks the (unchanged) raw body against the shared secret — validation succeeds.
6. The handler is invoked with `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body:, ...)`, causing the app to process attacker-supplied data under the victim shop's identity.

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
