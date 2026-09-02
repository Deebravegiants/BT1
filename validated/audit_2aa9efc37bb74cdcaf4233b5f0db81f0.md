## Title
Webhook `shop` Domain Is Not Covered by the HMAC Signature, Enabling Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature only over the raw request body, while the `shop` (tenant identity) field is read directly from an HTTP header that is never included in the signed content. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then blindly forwards this unauthenticated `shop` value to the app's webhook handler via `WebhookMetadata`. Because the app's `api_secret_key` is shared across every shop that has installed the app, any shop owner who can trigger a genuine webhook for their own store can relabel it as coming from a different shop, and the signature will still validate.

### Finding Description
The `to_signable_string` implementation used for HMAC verification returns only the raw body: [1](#0-0) 

The `shop` accessor, however, is derived purely from the `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header, which is not part of the signed content at all: [2](#0-1) 

`HmacValidator.validate` only checks the HMAC over `to_signable_string` (i.e. the body) against `Context.api_secret_key`: [3](#0-2) 

`Registry.process` validates this HMAC and then trusts `request.shop` as the tenant identity to hand to the app's handler, without any additional binding check: [4](#0-3) 

The broken identity binding is:
`hmac_valid_for(body, api_secret_key) == true` is being treated as proof of `shop == authenticated_shop`, when in fact the HMAC proves nothing about `shop` — it is orthogonal, unauthenticated header data.

Since `api_secret_key` is a single shared secret for the app across all merchant installations (not per-shop), any merchant that has installed the app can trigger a legitimate webhook for their own store (e.g. `orders/create`), capture the genuine `hmac-sha256` value Shopify computed for that body, and replay the same request to the app's webhook endpoint with the `shopify-shop-domain` header swapped to a different, victim shop's domain. `HmacValidator.validate` will still return `true` because it only checks the body, and `Registry.process` will invoke the app's handler with `WebhookMetadata#shop` set to the attacker-chosen victim domain.

### Impact Explanation
This breaks the tenant boundary the whole webhook subsystem is designed to enforce: `WebhookMetadata#shop` is the field host applications are documented/expected to rely on to know *which merchant* a webhook event belongs to (for looking up sessions, writing tenant-scoped data, etc.). An attacker who controls one legitimate shop can cause their own genuine, HMAC-valid webhook traffic to be attributed to an arbitrary other shop domain, resulting in cross-tenant data confusion/corruption in any host application that scopes behavior by `data.shop` — which is the intended and only documented use of that field.

### Likelihood Explanation
Any merchant that installs the app is, from the app's perspective, an "unprivileged" actor with respect to other tenants, and can freely trigger webhooks for their own shop (via ordinary store actions) and replay the request body/HMAC pair with a modified `shop` header value to any endpoint that exposes the webhook route. No access to `api_secret_key`, TLS interception, or social engineering is required — only the ability to intercept/observe one's own outbound webhook call and replay it with a different header, which is trivial for any authenticated merchant.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the HMAC-signed content, or otherwise cryptographically bind the `shopify-shop-domain` header value to the verified payload before trusting it as tenant identity — e.g., verify that the header-derived shop matches a shop associated with the specific installation/session expected to have triggered this webhook, rather than trusting the header outright once the body-only HMAC passes.

### Proof of Concept
1. App is installed on `attacker-shop.myshopify.com` and `victim-shop.myshopify.com` (same `client_id`/`api_secret_key`).
2. Attacker performs an action in `attacker-shop.myshopify.com` that triggers a webhook (e.g., `orders/create`) with body `B`. Shopify sends the request with headers including `shopify-hmac-sha256: HMAC(B, api_secret_key)` and `shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker intercepts this legitimate call to their own endpoint and re-sends it to the app's webhook endpoint, keeping body `B` and the same `shopify-hmac-sha256` value, but changing `shopify-shop-domain` to `victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `HMAC(B, api_secret_key)` against the (unchanged) body `B`. [5](#0-4) 
5. The app's handler is invoked with `WebhookMetadata#shop == "victim-shop.myshopify.com"` even though the event actually originated from `attacker-shop.myshopify.com`, causing the host application to process/store attacker-controlled data under the victim shop's identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L13-31)
```ruby
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
