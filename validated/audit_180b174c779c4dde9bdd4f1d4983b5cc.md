## Analysis

I found a valid analog in this gem's webhook verification code, matching the report's core bug class: **a field acted on by application logic that is not covered by the cryptographic signature meant to authenticate the request.**

### Root cause [1](#0-0) 

`ShopifyAPI::Webhooks::Request` extracts `hmac` from the `hmac-sha256` header, `shop` from the `shop-domain` header, and defines `to_signable_string` to return **only `@raw_body`** — the HMAC signature never covers `topic`, `shop`, `webhook_id`, or `api_version`. Verification is performed with `Utils::HmacValidator.validate(request)`, which calls `verifiable_query.to_signable_string` (the body only) against the secret. [2](#0-1) 

`Registry.process` validates the HMAC (over the body only) and then unconditionally trusts `request.shop` (an unauthenticated header) to build `WebhookMetadata`, which is handed to the app's webhook handler as the tenant identity for that webhook.

### Why this is exploitable without any secret

An unprivileged internet user who owns their own legitimate, installed Shopify store can trigger webhooks on their own shop and thus legitimately obtain a **valid `(body, hmac)` pair** signed with the app's `client_secret` (the secret is shared across all shops for a given app — this is a real characteristic of Shopify's webhook HMAC scheme). They can then replay that same body+HMAC to the app's webhook endpoint while substituting the `shop-domain` header to name a **different (victim) shop**. Because `shop` is not part of `to_signable_string`, the HMAC check in `HmacValidator.validate` still passes, and `Registry.process` will dispatch the handler with `shop: <victim-shop>` even though the body content actually originated from the attacker's own shop.

This breaks the identity binding: **shop authenticated (implicitly, by virtue of a valid signature existing) ≠ shop actually bound by that signature**. If a host application uses `WebhookMetadata#shop` to select the tenant record to update/query (a documented, expected usage pattern for this field), an attacker can inject/attribute their own webhook payload to another merchant's tenant — a cross-tenant confusion primitive achievable entirely with an unprivileged Shopify store and no leaked secrets.

### Title
Webhook `shop-domain` Header Not Covered by HMAC Enables Cross-Tenant Webhook Spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only signs the raw webhook body, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated HTTP headers. `Webhooks::Registry.process` trusts the header-derived `shop` value once body HMAC validation succeeds, allowing an attacker who legitimately owns any shop with the app installed to replay a validly-signed body under a spoofed `shop-domain` header naming a different, victim shop.

### Finding Description
`Utils::HmacValidator.validate` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it to the `hmac` header [3](#0-2) . For webhooks, `to_signable_string` returns only `@raw_body` [4](#0-3) , so the `shop`, `topic`, `webhook_id`, and `api_version` headers are entirely outside the authenticated scope, yet `Registry.process` uses them to build the `WebhookMetadata` passed to the app's handler [2](#0-1) . Because the app's `client_secret` used for HMAC signing is the same across all of the app's installed shops, any shop owner with the app installed can obtain a validly-signed `(body, hmac)` pair for their own shop and resend it with a different `shop-domain` header value, with the HMAC check still passing.

### Impact Explanation
This meets the "cross-tenant access" criterion: it allows an attacker who controls one tenant (their own installed shop) to make the gem report webhook data as originating from an arbitrary different tenant to the host application's handler, without possessing any victim credentials, tokens, or the app's `client_secret` itself.

### Likelihood Explanation
Requires only that the attacker install the target app on a shop they control (or use one they already have) — no leaked secrets, no privileged access, and no host cooperation beyond using the documented `WebhookMetadata#shop` field as intended.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` in the HMAC-signed material (or otherwise cryptographically bind them to the payload), or clearly document that `request.shop`/`WebhookMetadata#shop` is unauthenticated and must be cross-validated by the host application against the shop's known registration/session before being trusted for tenant-scoped operations.

### Proof of Concept
1. Attacker installs app on `attacker-shop.myshopify.com`; app registers a webhook.
2. Shopify sends a webhook to the app with `x-shopify-hmac-sha256: HMAC(secret, body)` and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker captures `(body, hmac)` from step 2 (their own traffic/logs) and re-sends a POST to the app's webhook endpoint with the same body and hmac, but `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `HmacValidator.validate` passes (body unchanged), `Registry.process` dispatches `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker's body>, ...)` to the handler [5](#0-4) , causing tenant-scoped confusion in any handler that trusts `shop`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
