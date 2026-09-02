## Finding

### Title
Webhook shop-domain header is trusted as tenant identity without being covered by the HMAC signature, enabling cross-shop webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC-verifiable signable string from the raw body only. The `X-Shopify-Shop-Domain` header (as well as topic/webhook-id/api-version) is never included in the signed material, yet `Registry.process` passes that unauthenticated header value straight through to the app's webhook handler as the trusted shop/tenant identifier.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor simply reads an unauthenticated header: [2](#0-1) 

`Registry.process` validates only `Utils::HmacValidator.validate(request)` (i.e., HMAC over the body against `Context.api_secret_key`), and then immediately forwards `request.shop` to the registered handler as the authoritative tenant identifier: [3](#0-2) 

`HmacValidator.validate` only compares the HMAC over whatever `to_signable_string` returns: [4](#0-3) 

The identity binding broken is: `hmac_verified_bytes (raw_body) != shop_identity_used_by_handler (X-Shopify-Shop-Domain header)`. Because the app's `api_secret_key` is a single shared secret across all shops that install the app (it is not shop-specific), any body+HMAC pair that validates for one shop validates identically regardless of which shop-domain header accompanies it. An unprivileged internet user who has legitimate access to a genuine webhook delivery for their own shop (e.g., by installing the app on their own free/dev store and capturing an `app/uninstalled`, `shop/update`, or other webhook payload+HMAC) can resend that exact body and HMAC to the app's webhook endpoint while substituting an arbitrary victim's `X-Shopify-Shop-Domain` (or `X-Shopify-Hmac-Sha256`/`X-Shopify-Topic` combination the app supports). `Registry.process` will accept it as valid (HMAC still matches, since it never covered the shop header) and hand the handler a `WebhookMetadata` claiming to be the victim shop.

### Impact Explanation
Because host applications are documented to rely on `WebhookMetadata#shop` (or `request.shop`) as the tenant key to look up/act on per-shop state (e.g., delete session/access-token records on `app/uninstalled`, update shop settings, trigger shop-scoped business logic), an attacker can forge webhook deliveries attributed to a victim shop domain using self-obtained valid payload/HMAC pairs. This is a cross-tenant confusion/spoofing primitive — the impact bucket matches "cross-tenant access" (Critical) since it lets one tenant's authenticated webhook event be replayed as if it originated from another tenant.

### Likelihood Explanation
Likelihood is realistic but bounded: the attacker needs at least one valid body+HMAC pair, which they can generate cheaply and repeatably by installing the app themselves (a normal unprivileged action for any Shopify developer/merchant) and capturing any webhook topic the app subscribes to. No access token, `client_secret`, or privileged account is required — only participation as a normal merchant of the target app, then a forged HTTP POST to the app's public webhook endpoint with a substituted shop header.

### Recommendation
Bind the shop identity into the verified material, e.g. include `shopify-shop-domain` (and ideally `shopify-webhook-id`/`shopify-topic`) in the HMAC-covered signable string, or independently verify that the shop asserted in the header corresponds to a session/shop that the app actually has installed and is expecting for that webhook_id, before trusting `request.shop` in `WebhookMetadata`.

### Proof of Concept
1. Install the target app on an attacker-controlled Shopify dev store (`attacker-shop.myshopify.com`).
2. Trigger a webhook delivery the app subscribes to (e.g. `app/uninstalled`) and capture the raw request body plus `X-Shopify-Hmac-Sha256` header — both are valid because they were computed by Shopify against the app's shared `api_secret_key`.
3. Replay a POST to the app's webhook endpoint with the identical body and HMAC header, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` computes `Utils::HmacValidator.validate(request)` over `raw_body` only (`lib/shopify_api/webhooks/request.rb:35-38`), which still matches; the handler executes with `shop: "victim-shop.myshopify.com"`, causing the app to perform shop-scoped actions (e.g., token/session deletion) against the victim tenant it never actually initiated.

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
