This confirms the core finding: `Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , so the HMAC computed by `Utils::HmacValidator.validate` covers only the request body [2](#0-1) . Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from unauthenticated HTTP headers [3](#0-2)  and are passed unmodified into `WebhookMetadata` that the host app's handler consumes as the tenant identity [4](#0-3) .

### Title
Webhook `shop-domain` (and `topic`/`webhook-id`/`api-version`) headers are not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant-identifying `shop` value (and `topic`, `webhook_id`, `api_version`) from HTTP headers that are never included in the HMAC signature computation, while `Webhooks::Registry.process` trusts and forwards these unauthenticated header values to the host application's handler as verified webhook metadata.

### Finding Description
`Utils::HmacValidator.validate` verifies a `VerifiableQuery` by recomputing an HMAC over `to_signable_string` and comparing it to the supplied `hmac` value using `OpenSSL.secure_compare` [2](#0-1) . For `Webhooks::Request`, `to_signable_string` returns only `@raw_body` [1](#0-0) . The `shop`, `topic`, `api_version`, and `webhook_id` accessors, however, are read directly from the `shopify-*`/`x-shopify-*` headers with no cryptographic binding to the signed body [5](#0-4) .

`Webhooks::Registry.process` only checks `Utils::HmacValidator.validate(request)` (i.e., that the body's HMAC is valid) before dispatching `request.shop`, `request.topic`, and `request.webhook_id` straight into `WebhookMetadata` passed to the app's registered handler [4](#0-3) .

This breaks the intended binding `hmac_signed(body) == hmac_signed(body, shop)`: the gem's contract implies that a request whose HMAC validates originates authentically from the shop identified by `request.shop`, but in reality the HMAC only proves the body's integrity, not the header's authenticity. An unprivileged internet user who legitimately receives one authentic webhook delivery for a shop they control (e.g., by installing the app on their own development/test store) obtains a `(raw_body, hmac)` pair that is valid for that body regardless of the `shop-domain`/`topic`/`webhook-id` headers sent alongside it, since those headers play no role in the signature. The attacker can then replay the exact same body and HMAC to the app's webhook endpoint while substituting a different `shop-domain` header value (impersonating a victim shop) or a different `webhook-id`/`topic`, and `Registry.process` will treat it as a validly-authenticated webhook for the spoofed shop.

### Impact Explanation
Any host application built on this gem that uses `WebhookMetadata#shop` (populated straight from `request.shop`) to select which tenant's session/data-store to act on — the standard integration pattern shown in this gem's own webhook handler examples — can be made to attribute an attacker-controlled body to an arbitrary, unrelated shop. This is a cross-tenant boundary violation: `Registry.process` accepts as "verified for shop=X" a payload whose authenticity was only ever established for the body, not for X. Depending on the webhook topic (e.g., `customers/data_request`, `shop/redact`, `app/uninstalled`, order/customer data topics), this can trigger destructive or data-disclosing tenant-scoped actions against a shop the attacker does not control.

### Likelihood Explanation
The attack requires only: (1) installing the app on any shop the attacker controls to receive one legitimately signed webhook, and (2) sending an HTTP POST to the app's public webhook endpoint with the same body/HMAC but a spoofed `x-shopify-shop-domain` (and optionally `x-shopify-topic`/`x-shopify-webhook-id`) header — no access to `api_secret_key`, access tokens, or any privileged credential is needed, satisfying the "unprivileged internet user" bar.

### Recommendation
Include `shop`, `topic`, and `webhook_id` (all header-derived fields the application relies on) in the signable/verifiable material, or otherwise cryptographically bind them to the body before trusting them in `Registry.process`/`WebhookMetadata`. At minimum, document and enforce that host applications must not use `request.shop`/`request.topic` for authorization decisions without independently confirming the shop identity (e.g., cross-checking against a known/expected shop for that webhook subscription) since the gem itself does not authenticate these header values.

### Proof of Concept
1. Register/install the target app on attacker-owned shop `attacker.myshopify.com`; receive a genuine webhook POST with body `B` and valid header `x-shopify-hmac-sha256: H` (where `H = HMAC-SHA256(secret, B)`), plus `x-shopify-shop-domain: attacker.myshopify.com`.
2. Replay an HTTP POST to the app's webhook endpoint with the identical body `B` and header `x-shopify-hmac-sha256: H`, but set `x-shopify-shop-domain: victim.myshopify.com` (and optionally change `x-shopify-topic`/`x-shopify-webhook-id`).
3. `Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes the HMAC over `@raw_body` (`to_signable_string`) [1](#0-0)  — validation succeeds because `B` and `H` are unchanged.
4. The handler is invoked with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` reporting `shop: "victim.myshopify.com"` [4](#0-3) , causing the host app to process attacker-controlled data as if it came from the victim's shop.

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
