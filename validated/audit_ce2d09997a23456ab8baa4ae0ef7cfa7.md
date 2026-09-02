### Title
Webhook shop identity spoofing via HMAC-unbound `shop-domain` header - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook by validating an HMAC over the raw request body only, but then trusts the `shop-domain` header — which is *not* covered by that HMAC — as the tenant identity passed to the app's webhook handler. This breaks the binding `hmac_verified_bytes == bytes_the_shop_field_is_taken_from`, allowing any user who can obtain one valid `(raw_body, hmac)` pair for the app (e.g. by installing the app on their own store and receiving a genuine webhook) to replay that pair to the app's public webhook endpoint while substituting an arbitrary victim `shop-domain`, causing the handler to process attacker-controlled data as if it belonged to the victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` and defines: [1](#0-0) 

`shop` is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header, while `to_signable_string` (the data that gets HMAC-verified) is only the raw body. `HmacValidator.validate` computes and compares the HMAC strictly against `to_signable_string`: [2](#0-1) 

`Registry.process` performs exactly this check and then forwards `request.shop` — the unauthenticated header value — into the handler as the tenant identifier: [3](#0-2) 

The equality that should hold is: *the shop attributed to a webhook == the shop whose secret produced the verified bytes*. Instead, only `hmac == HMAC(secret, raw_body)` is checked; `shop` is parsed from a sibling header that participates in no cryptographic binding at all. Any requester who already possesses one legitimately-signed `(raw_body, hmac)` pair for the app (trivial to obtain — install the app on an attacker-owned store and capture a real webhook, e.g. `app/uninstalled` or `shop/redact`) can POST that exact body/HMAC pair directly to the app's public webhook route while setting `shop-domain` to any victim shop. `HmacValidator.validate` passes because it never inspects the header, and `Registry.process` dispatches the handler with `shop: "victim-shop.myshopify.com"`.

### Impact Explanation
This is a cross-tenant identity-confusion primitive delivered entirely from this gem's own verification logic (not a host-app misuse): the gem itself asserts the webhook came from Shopify for the named shop, but never binds that name to the signed bytes. A host application that trusts `WebhookMetadata#shop` (the gem's own documented contract, see `docs/usage/webhooks.md`) to key data access, credential revocation, or GDPR compliance actions (`shop/redact`, `customers/redact`, `customers/data_request` are exactly the topics this gem marks `MANDATORY_TOPICS`) will act on another tenant's data on the word of an unauthenticated header. This satisfies "cross-tenant access" (Critical).

### Likelihood Explanation
Any developer/merchant who can install the target app on a store they control can generate a real, validly-signed webhook and replay its body/HMAC pair against a different `shop-domain`. No secrets, tokens, or privileged access to the victim are required — only network access to the app's public webhook endpoint and an install of the app on any (even brand-new, free) store.

### Recommendation
Include the shop domain (and ideally other routing headers such as `topic`/`webhook-id`) in the value that is HMAC-verified, or otherwise cryptographically bind the `shop-domain` header to the verified payload before it is handed to `WebhookHandler#handle`. At minimum, document that host applications must independently confirm `WebhookMetadata#shop` corresponds to a shop that has this app installed/an active session, since `Request#shop` is presently unauthenticated header data.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `evil.myshopify.com` and registers for `shop/redact` (or any mandatory topic).
2. Shopify legitimately delivers a webhook to the app: raw body `B`, header `X-Shopify-Hmac-Sha256: H` (HMAC over `B` using the app's real client secret), header `X-Shopify-Shop-Domain: evil.myshopify.com`.
3. Attacker captures `(B, H)` and issues a direct POST to the same public webhook endpoint with unchanged body `B` and header `H`, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `H == HMAC(secret, B)` — this still passes.
5. The registered handler is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)`, causing the host app to perform the `shop/redact` (or other) action against `victim.myshopify.com`'s stored data, even though `victim.myshopify.com` never sent this webhook.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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
