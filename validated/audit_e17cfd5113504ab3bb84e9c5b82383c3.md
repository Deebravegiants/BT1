Found a solid analog in the webhook processing path: the `shop` field used for tenant attribution is not covered by the HMAC signature check.This confirms the interface: any `VerifiableQuery` implementer only needs to expose `hmac` and `to_signable_string`. For `Webhooks::Request`, `to_signable_string` returns solely `@raw_body`, so headers (including `shop-domain`) are never covered by the HMAC that `Utils::HmacValidator.validate` checks.

### Title
Webhook shop-domain header is not covered by HMAC verification, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body via `Utils::HmacValidator.validate(request)`. The `shop` (tenant) value that the handler receives and acts on — `request.shop`, sourced from the `x-shopify-shop-domain`/`shopify-shop-domain` header — is never included in the signed payload. Anyone who can obtain one valid `(raw_body, hmac)` pair for their own shop (a normal, unprivileged consequence of installing the app) can replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `shop-domain` header, and the signature check will still pass.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` computes the HMAC exclusively over `to_signable_string` and compares it to the `hmac` header value — no other header, including `shop-domain`, participates in the digest: [2](#0-1) 

`Webhooks::Registry.process` performs this HMAC check and then immediately trusts `request.shop` (and other headers) to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

`Webhooks::Request#shop` is read directly from the `shop-domain` header with no cross-check against the signed body: [4](#0-3) 

The equality that should hold but doesn't: `shop used for tenant identification == shop covered by the HMAC digest`. Because `to_signable_string` only equals `@raw_body`, the `shop-domain` header is fully outside the authenticated boundary. An attacker who legitimately installs the app on their own shop receives real, correctly-signed webhooks (the HMAC is computed with the app's real `client_secret`, but the attacker only needs the resulting `(body, hmac)` pair, not the secret itself). They can replay that untouched `(body, hmac)` pair to the app's public webhook endpoint while swapping in a victim shop's domain in the `shop-domain` header. `HmacValidator.validate` still succeeds because the body is byte-identical, and `Registry.process` hands the handler a `WebhookMetadata` claiming the event came from the victim shop.

### Impact Explanation
This breaks the tenant boundary the gem is expected to enforce for webhook processing: an app relying on `request.shop`/`WebhookMetadata#shop` to key persistence, deduplication, entitlements, or cross-tenant data writes can be made to process a self-generated payload as if it belongs to a shop the attacker doesn't control. Depending on how the host app uses the `shop` field (e.g., writing order/webhook data keyed by shop, or triggering shop-specific side effects), this can lead to cross-tenant data corruption or spoofed events attributed to another merchant — a High severity cross-tenant boundary violation.

### Likelihood Explanation
Likelihood is meaningful but constrained: the attacker must control at least one shop with the app installed (an ordinary, unprivileged action — anyone can install a public/dev app) to obtain a valid `(raw_body, hmac)` pair, and must know or guess a victim's `.myshopify.com` domain (publicly discoverable). No `api_secret_key`, access token, or other credential of the app is required — only receipt of a webhook the attacker's own shop is entitled to receive. The webhook endpoint itself is, by design, publicly reachable (Shopify must be able to POST to it without prior authentication), so no additional access is required to reach `Registry.process`.

### Recommendation
Bind the identity used for tenant attribution to the authenticated payload. Options: include the `shop-domain` (and ideally `topic`/`webhook-id`) header value in the HMAC-signed material verified by `HmacValidator`, or require the host application to independently correlate the header-derived `shop` against a `shop`/`myshopify_domain` field embedded in the JSON body before trusting it, and reject requests where they diverge.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers an event (e.g., creates an order) — Shopify delivers a legitimately signed webhook: `body = B`, header `x-shopify-hmac-sha256 = H` (`H` = valid HMAC-SHA256 of `B` under the app's real secret), `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker replays the exact same request to the app's webhook endpoint but changes only the header: `x-shopify-shop-domain: victim-shop.myshopify.com` (body `B` and `hmac` header `H` unchanged).
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...shop-domain: "victim-shop.myshopify.com", hmac-sha256: H})` is constructed; `Utils::HmacValidator.validate` succeeds because it only checks `H` against `B`.
4. `Registry.process` calls the app's handler with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: JSON.parse(B), ...)`, causing the app to process attacker-controlled data as if it originated from the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
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

        private

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
