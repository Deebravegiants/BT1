### Title
Webhook shop identity spoofing via unauthenticated `shop-domain` header — ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC over the raw body only, while the `shop` value that the app later trusts as the tenant identifier is read from an HTTP header that is never included in the HMAC-covered bytes. This breaks the binding `shop authenticated by HMAC == shop used as the tenant/session key`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header, independent of the signed bytes: [2](#0-1) 

`Registry.process` validates the HMAC (which only proves the *body* was produced with the app's shared secret) and then builds `WebhookMetadata` using `request.shop`, the unauthenticated header value, which is passed directly to the app's handler as the tenant identity: [3](#0-2) 

`HmacValidator.validate` / `validate_signature` only compares the HMAC of `to_signable_string` (the body) against the app's shared `api_secret_key`: [4](#0-3) 

Because the `api_secret_key` is shared by the app across **all** installed shops (it's an app-level secret, not a per-shop one), any body that is validly signed for one shop is *also* validly signed for every other shop using the same app. An unprivileged merchant who has installed the app on their own store can trigger a webhook with attacker-chosen body content (e.g., by creating an order with attacker-controlled fields), capture the valid `hmac-sha256` + raw body pair Shopify sent to the app, then replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` still succeeds (it never looked at the header), and `Registry.process` calls the app's handler with `WebhookMetadata.shop` set to the victim's domain rather than the attacker's own shop.

**Binding broken:** `shop covered by HMAC` ≠ `shop used as session/tenant key` — the HMAC binds only the body; the tenant identity (`shop`) is taken from an out-of-band, unauthenticated header.

### Impact Explanation
Any app built on top of this gem that keys its per-tenant state (e.g., which merchant's order/customer/inventory record to update, which merchant's session/store to attribute the webhook to) off `WebhookMetadata#shop` can be made to write attacker-supplied data into another tenant's context — a cross-tenant data-integrity/confusion issue. This matches the Critical bucket ("cross-tenant access") in the rules, since the vulnerability lets one merchant's request be attributed to an arbitrary other merchant of the same app without any credential belonging to that other merchant.

### Likelihood Explanation
Medium. It requires only an unprivileged party who has installed the target app on their own store (a normal, unprivileged action) and can trigger a webhook whose body is (partly) attacker-influenced (many webhook topics, e.g. `orders/create`, `customers/update`, carry merchant-controlled field values). No access to the app's `client_secret`, access tokens, or any other privileged credential is required — only observation of one's own legitimately-delivered webhook HMAC/body pair and the ability to POST an HTTP request to the app's public webhook endpoint with a modified header.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) inside the HMAC-signed material, or otherwise cryptographically bind the `shop` value to the verified payload before it is handed to `WebhookMetadata`/the app's handler, e.g. by verifying `request.shop` against Shopify's `X-Shopify-Shop-Domain` only after independently confirming it corresponds to an install that actually owns that HMAC (for instance, per-shop secret verification, or requiring the caller to look up the session by `shop` before trusting webhook content for it, combined with documentation flagging that `shop` is not covered by the HMAC).

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` (unprivileged, self-service).
2. Attacker triggers a webhook whose body they control (e.g., creates an order with `note`/custom fields containing malicious payload). Shopify sends: 
   `x-shopify-hmac-sha256: <valid HMAC of body B under app's api_secret_key>`, `x-shopify-shop-domain: attacker-shop.myshopify.com`, body `B`.
3. Attacker captures this HMAC/body pair and resends the same request to the app's public webhook endpoint, only changing the header to `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb`) succeeds because it only checks `body` against the shared secret.
5. `ShopifyAPI::Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb:189-200`) invokes the app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: B, ...)`, causing the app to process attacker-controlled data `B` as if it belonged to `victim-shop`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/webhooks/registry.rb (L189-200)
```ruby
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
