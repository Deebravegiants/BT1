### Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) headers are not covered by the HMAC, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` claims to "verify the request did indeed come from Shopify" before invoking the app's webhook handler, but the HMAC signature only covers the raw request body. The `shop` domain (and `topic`, `webhook_id`, `api_version`) delivered via headers are never included in the signed data, so an attacker who can obtain one valid `(body, hmac)` pair can replay it with an arbitrary `shop` header value and have it accepted as authentic for a different tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

and the `shop`, `topic`, `webhook_id`, `api_version` accessors are pulled straight from unauthenticated headers: [2](#0-1) 

`Registry.process` validates only this body-only HMAC via `Utils::HmacValidator.validate(request)` and then forwards the header-derived `shop` unchanged to the app's handler: [3](#0-2) 

`Utils::HmacValidator.validate_signature` recomputes the HMAC over `verifiable_query.to_signable_string` (the body only) and compares it to the received `hmac`: [4](#0-3) 

The identity binding that is broken: `shop domain verified by HMAC` ≠ `shop domain acted upon by the handler`. The equality the gem needs but does not enforce is `hmac_signed_bytes ⊇ {body, shop}`, but in fact `hmac_signed_bytes = {body}` only. Because the same `client_secret`-derived HMAC key is shared across every shop that installs the app, any body+hmac pair valid for tenant A remains cryptographically valid when replayed with a `shop-domain` header claiming to be tenant B — the signature check in `HmacValidator.validate_signature` has no way to detect the substitution.

The gem's own documentation reinforces the false assumption that the full request (including `shop`) is authenticated: "This will verify the request did indeed come from Shopify" and shows a canonical handler pattern that trusts `data.shop` directly, e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`, as shown in `docs/usage/webhooks.md`. Nothing in `WebhookMetadata` or `Registry.process` signals to implementers that `shop` requires independent verification against a known/installed-shops list.

### Impact Explanation
Any app that follows the documented pattern and uses `data.shop` from `WebhookMetadata` to select/mutate the tenant's records (the exact pattern shown in the gem's own docs) is exposed to cross-tenant data confusion/injection: an attacker who legitimately installs the app on their own (attacker-controlled) shop can capture one genuine webhook delivery (body + hmac), then replay that exact body/hmac pair to the app's webhook endpoint while substituting the `shopify-shop-domain` (and optionally `shopify-topic`/`shopify-webhook-id`) header to name a victim shop. `Registry.process` will pass HMAC validation (since the body is unchanged) and hand the attacker-chosen `shop` to the handler, causing the app to act as if the victim shop sent that payload. Depending on the handler's logic, this can corrupt or leak data associated with another merchant's tenant record — a cross-tenant access issue.

### Likelihood Explanation
The attacker only needs to be an unprivileged internet user capable of installing the app on their own store (a normal, low-privilege action available to anyone), capture one webhook delivery to their own endpoint, and then send a crafted HTTP request with the recycled body/hmac and forged `shop` header to the app's public webhook route. No access to `api_secret_key`, tokens, or victim credentials is required, and the gem provides no shop-domain cross-check to prevent it, making this readily reachable.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the value that is actually verified: either include these header values in the signable string used for HMAC computation, or have `Registry.process` independently confirm that `request.shop` corresponds to a shop with an active session/installation known to the app before dispatching to the handler. At minimum, update `WebhookMetadata`/documentation to explicitly warn that `shop` is unauthenticated header data and must be cross-checked by the host app against its own installed-shops record before being trusted.

### Proof of Concept
1. Install the target app on an attacker-controlled shop `attacker.myshopify.com` and trigger any subscribed webhook topic (e.g. `orders/create`).
2. Capture the raw HTTP request Shopify sends to the app's webhook endpoint, noting the body and the `x-shopify-hmac-sha256` header (valid HMAC over that body using the app's shared `client_secret`).
3. Replay the identical body and `x-shopify-hmac-sha256` value to the same endpoint, but set `x-shopify-shop-domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because the body/hmac pair is unchanged, as seen in [3](#0-2) 
5. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and the attacker's body, and — following the exact pattern shown in the gem's own documentation — acts on/persists this data under the victim's tenant.

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
