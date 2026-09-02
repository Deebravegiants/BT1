### Title
Webhook shop/topic/webhook-id are not covered by the HMAC signature, allowing cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies the authenticity of an incoming webhook by validating an HMAC computed only over the raw request body [1](#0-0) . The `shop`, `topic`, `webhook_id` and `api_version` values that identify *which tenant* the webhook belongs to are pulled straight from unauthenticated HTTP headers and are never included in the signed bytes [2](#0-1) . This breaks the equality that the HMAC is supposed to guarantee: `hmac_verified_bytes (raw_body)` ≠ `bytes_the_handler_trusts_for_tenant_routing (shop header)`.

### Finding Description
`ShopifyAPI::Webhooks::Request#hmac` reads the `shopify-hmac-sha256` header and `#to_signable_string` returns only `@raw_body`: [3](#0-2) [4](#0-3) 

`#shop`, `#topic`, `#webhook_id`, and `#api_version` are read from separate headers that are not part of `to_signable_string`: [5](#0-4) 

`HmacValidator.validate` only checks `verifiable_query.to_signable_string` (i.e. the body) against the secret; it never touches the shop/topic/webhook-id headers: [6](#0-5) 

`Registry.process` validates only that HMAC, then forwards the *unauthenticated* `request.shop` (and `request.topic`, `request.webhook_id`, `request.api_version`) straight into `WebhookMetadata`, which is handed to the app's handler as the tenant identity: [1](#0-0) 

The `client_secret`/`api_secret_key` used to compute the HMAC is a single, app-wide secret shared by every shop that has installed the app (it is not per-shop) [7](#0-6) . Consequently, any merchant who installs the app can trivially obtain a body+HMAC pair that is valid for the app's shared secret, simply by triggering a real event on their own store (e.g. creating an order) and capturing the resulting genuine webhook delivery. Because `shop-domain` (and `topic`/`webhook-id`) are not bound into the signed bytes, that attacker-controlled body+HMAC pair remains valid no matter what `X-Shopify-Shop-Domain` header value accompanies it. The attacker can therefore replay the exact same body and HMAC while substituting a victim shop's domain in the `shop-domain` header, and `Registry.process` will still accept it and dispatch the handler with `shop: <victim-shop>`.

This is precisely the "shop authenticated vs. shop stored/used as tenant key" binding break: the equality `hmac_verified_shop == shop_used_for_tenant_routing` does not hold, because no such `hmac_verified_shop` value exists at all — the signature never covers the shop.

### Impact Explanation
This enables cross-tenant webhook forgery. The gem's own documented usage pattern is to trust `data.shop` for routing work to the correct tenant (`perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`, per `docs/usage/webhooks.md`). An attacker who is a legitimate installer of the vulnerable app (i.e., an unprivileged internet user relative to any *other* merchant/tenant of the same app) can forge a webhook event that the host application will attribute to a victim shop it has no relationship to, since the HMAC check passes and the shop identity is taken on faith from a header outside the signed payload. This is a cross-tenant integrity/access issue: attacker-chosen body content (from a real webhook they legitimately received) gets processed under a victim shop's identity.

### Likelihood Explanation
Any user who can install the app on their own store (a normal, unprivileged flow) can capture a genuine, validly-signed webhook body/HMAC pair without needing the app's `client_secret`, access tokens, or any other privileged material — they simply receive it as their own installed app's webhook delivery. Replaying it with a modified `Shop-Domain` header is a single crafted HTTP request against the app's public webhook endpoint. No credentials beyond "being any merchant using the app" are required.

### Recommendation
Include the tenant-identifying headers (`shop-domain`, and ideally `topic`/`webhook-id`) in the HMAC-verified material, or otherwise cryptographically bind them to the body before trusting them, e.g. by having `VerifiableQuery#to_signable_string` incorporate `shop`/`topic` alongside the raw body, or by validating that the shop header corresponds to a shop for which the currently-registered webhook subscription id (`webhook_id`) is actually known/expected. At minimum, document prominently that `data.shop` in `WebhookMetadata` is not authenticated by the HMAC and must not be used alone to select a tenant record without additional verification (e.g., cross-checking against a known list of webhook ids registered per shop).

### Proof of Concept
1. Attacker installs the vulnerable app on their own store `attacker.myshopify.com` (a normal, permitted install).
2. Attacker triggers a real event (e.g. creates an order) causing Shopify to deliver a genuine webhook to the app's endpoint with a valid `X-Shopify-Hmac-Sha256` computed over the raw body using the app's shared `client_secret`, and headers `X-Shopify-Shop-Domain: attacker.myshopify.com`, `X-Shopify-Topic: orders/create`.
3. Attacker captures that raw body and the `X-Shopify-Hmac-Sha256` value.
4. Attacker POSTs the identical raw body and `X-Shopify-Hmac-Sha256` header to the same endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
5. `ShopifyAPI::Webhooks::Request.new` parses the request; `Utils::HmacValidator.validate` recomputes the HMAC over `@raw_body` only and it matches, per `lib/shopify_api/utils/hmac_validator.rb` L12-31.
6. `Registry.process` calls the app's handler with `WebhookMetadata.new(topic: "orders/create", shop: "victim.myshopify.com", body: <attacker's order data>, ...)`, per `lib/shopify_api/webhooks/registry.rb` L188-199 — the host application now processes attacker-supplied data under the victim tenant's identity.

### Citations

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
