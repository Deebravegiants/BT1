I found a concrete identity-binding gap: `Webhooks::Request` computes its HMAC over `@raw_body` only, while `shop`, `topic`, and `webhook_id` are read from unauthenticated headers and passed downstream to the handler as trusted tenant-identifying metadata.This confirms the finding: `ShopifyAPI::Webhooks::Registry.process` explicitly validates that "the request did indeed come from Shopify" via HMAC, then hands `request.shop` (header-derived, unsigned) to the app's handler as trusted tenant identity, documented in `docs/usage/webhooks.md:125` and `docs/usage/webhooks.md:10-17`.

### Title
Webhook tenant identity (`shop` header) is not covered by HMAC verification, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `ShopifyAPI::Utils::HmacValidator.validate` verifies the HMAC exclusively against that body [1](#0-0) . However, `shop`, `topic`, and `webhook_id`, which the library treats as the authenticated identity of the webhook, are read from unauthenticated HTTP headers that are never included in the signable string [2](#0-1) . `Registry.process` only checks `Utils::HmacValidator.validate(request)` before forwarding `request.shop` to the app's handler as trusted tenant metadata [3](#0-2) .

### Finding Description
The binding that should hold is: `hmac_verified_bytes == bytes_that_determine_tenant`. In this gem that equality is broken — `hmac_verified_bytes == raw_body` while `bytes_that_determine_tenant == headers["shopify-shop-domain"]`, an entirely separate, unsigned channel [4](#0-3) .

Because a single Shopify app has one `api_secret_key` shared across every installing merchant, any merchant who installs the app can capture a genuine, correctly-signed webhook delivery for their own shop (body + `X-Shopify-Hmac-Sha256` signature). Since the signature covers only the JSON body — never the `shop-domain`, `topic`, or `webhook-id` headers — that attacker can resend the identical body/signature pair to the app's webhook endpoint while substituting the `shop-domain` header (and optionally `topic`/`webhook-id`) with a victim shop's domain. `Utils::HmacValidator.validate` recomputes the HMAC over `to_signable_string` (the body) and finds it valid, since the body was not modified [5](#0-4) . `Registry.process` then proceeds to call the registered handler with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)`, passing the attacker-controlled `shop` value through as if it were authenticated [6](#0-5) .

The library's own documentation instructs handler authors to trust `data.shop` directly to route/attribute the webhook (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`), reinforcing that this field is meant to be an authenticated tenant identifier [7](#0-6) .

### Impact Explanation
This breaks the tenant-isolation identity binding the report's bug class targets: a value that is acted upon (here, "which shop this webhook belongs to") is not covered by the cryptographic check that is supposed to authenticate the message. A malicious merchant/installer of the app can forge webhook deliveries that the host application will process as though they originated from a different, victim shop — leading to cross-tenant data confusion in the host app's webhook processing pipeline (e.g. writing/mutating data keyed by the spoofed shop, or triggering `shop/redact`/`customers/redact` compliance flows against the wrong tenant). This satisfies the High-impact category of a scope/tenant-binding check that answers permissively.

### Likelihood Explanation
Exploitability only requires the attacker to be a legitimate (even trial) installer of the target app — no leaked credentials, TLS interception, or privileged access is needed. They obtain a valid body+HMAC pair simply by triggering any webhook topic on their own store, then replay it against the app's public webhook endpoint with a forged `shop-domain` header. This is a low-effort, repeatable attack path fully within the "unprivileged internet user" threat model.

### Recommendation
Bind the identity fields into the verified payload, or otherwise ensure `Registry.process` cannot be fooled by header/body mismatch:
- Require the receiving app to independently confirm that `request.shop` corresponds to a shop for which the app holds an active session/access token before trusting it, and reject unknown/mismatched shops.
- Where possible, cross-check the `shop-domain` header against shop-specific webhook secrets (if using per-shop secrets) rather than a single app-wide secret, or document explicitly that `request.shop`/`request.topic` are unauthenticated and must be independently verified by the host application before use.
- Consider including a canonicalized representation of the critical headers (`shop-domain`, `topic`, `webhook-id`) in the value passed to `HmacValidator`, if Shopify's webhook signature scheme is extended to support it, so the signature binds the full authenticated context.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` and triggers a webhook (e.g. `orders/create`), capturing the raw POST body `B` and header `X-Shopify-Hmac-Sha256: H` sent by Shopify.
2. Attacker POSTs to the app's webhook endpoint with body `B` unchanged, header `X-Shopify-Hmac-Sha256: H` unchanged, but `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...shop-domain: "victim-shop.myshopify.com", hmac-sha256: H...})` is constructed; `to_signable_string` returns `B` only [1](#0-0) .
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(api_secret_key, B)` and compares to `H` — this matches because `B` and `H` are the original genuine pair [8](#0-7) .
5. The registered handler is invoked with `WebhookMetadata` where `shop == "victim-shop.myshopify.com"`, even though the webhook actually originated from the attacker's own shop and Shopify never sent any webhook for the victim shop [6](#0-5) .

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

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```
