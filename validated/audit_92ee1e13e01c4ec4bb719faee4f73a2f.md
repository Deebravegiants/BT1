### Title
Webhook `shop` (tenant) identifier is not covered by the HMAC signature, allowing cross-tenant confusion in `ShopifyAPI::Webhooks::Registry.process` - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from unauthenticated HTTP headers [2](#0-1) . `Registry.process` validates the HMAC against the body only and then hands the header-derived `shop` value directly to the host application's handler as the tenant identifier [3](#0-2) . The equality that should hold — "the shop the HMAC authenticates" == "the shop the handler acts on" — is broken because the HMAC never binds the shop header at all.

### Finding Description
`ShopifyAPI::Utils::HmacValidator.validate` calls `verifiable_query.to_signable_string`, and for webhook requests that method is `@raw_body` alone [1](#0-0) [4](#0-3) . The `shop` accessor used for tenant routing is derived purely from the `x-shopify-shop-domain`/`shopify-shop-domain` header [5](#0-4) , which is never included in the signed content. `Registry.process` raises only if the body-HMAC fails, then constructs `WebhookMetadata` using the unverified `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version`, and passes it to the app-supplied handler as the authoritative tenant/topic context [3](#0-2) . Because the app's shared `api_secret_key` (`Context.api_secret_key`) is the same across every shop that installs the app, and the signed content is only the JSON body, an attacker who has captured or can generate one valid `(body, hmac)` pair for Shop A can replay that same body+hmac to the app's webhook endpoint while substituting `x-shopify-shop-domain: shop-b.myshopify.com`. `Registry.process` will report a valid HMAC (body matches) and dispatch `WebhookMetadata.new(shop: "shop-b.myshopify.com", ...)` to the handler, i.e., attacker-controlled tenant binding despite a "verified" signature.

### Impact Explanation
Any app built on this gem that trusts `WebhookMetadata#shop` (or `#topic`/`#webhook_id`) as an authenticated tenant/topic identifier — which is the documented usage pattern shown in `docs/usage/webhooks.md` — can be tricked into processing webhook payloads under the wrong shop's identity, e.g., writing/deleting data keyed by the spoofed shop, or misrouting order/customer data across tenants. This is a cross-tenant confusion resulting from a broken identity binding (HMAC covers bytes of the body, not the header fields the code actually keys authorization on), matching the "Critical - cross-tenant access" category since the shop identity that gates per-tenant data handling is forgeable independent of the signature check.

### Likelihood Explanation
Exploitation requires only a single legitimately observed `(raw_body, hmac)` pair from the target app (e.g., from any shop, including the attacker's own trial install, or a leaked/replayed webhook), plus the ability to POST to the app's public webhook endpoint with attacker-chosen headers — no access token, `api_secret_key`, or privileged account is needed, satisfying the unprivileged-internet-user threat model. Because `HmacValidator.validate` and `Request#to_signable_string` never look at the shop header at all, the check is deterministic and always passes for a replayed body regardless of which shop header is sent.

### Recommendation
Include the tenant-identifying header (`shop`) — and ideally `topic`/`webhook_id`/`api_version` — as part of the signed content that `to_signable_string` returns for webhook `Request` objects, or otherwise cryptographically bind them (e.g., verify the shop against an independently-known list of installed shops before dispatching) before constructing `WebhookMetadata` in `Registry.process`.

### Proof of Concept
1. App installs on `shop-a.myshopify.com`; Shopify sends a legitimate webhook: body `B`, header `x-shopify-hmac-sha256: HMAC(secret, B)`, `x-shopify-shop-domain: shop-a.myshopify.com`.
2. Attacker captures/observes this `(B, HMAC)` pair (e.g., by installing the same app as an unprivileged test merchant, or from a replayable webhook the app itself will retry).
3. Attacker POSTs to the app's public webhook endpoint the same body `B` and same `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: shop-b.myshopify.com` (a victim tenant).
4. `Registry.process` runs `Utils::HmacValidator.validate(request)` [6](#0-5)  — this only recomputes HMAC over `B`, so it passes.
5. `Registry.process` dispatches `WebhookMetadata.new(topic: request.topic, shop: "shop-b.myshopify.com", body: ..., ...)` to the app's handler [7](#0-6) , causing the app to process shop A's payload as if it belongs to shop B.

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
