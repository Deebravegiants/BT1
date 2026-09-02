### Title
Webhook `shop` (and `topic`/`webhook_id`) headers are trusted without being covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates only the webhook's raw body via HMAC, but then trusts the unauthenticated `shop-domain`, `topic`, and `webhook-id` headers when building the data passed to the app's handler. An attacker who can obtain any single genuine `(body, hmac)` pair for the app (e.g. by triggering a webhook to their own installed shop) can replay that body to the app's webhook endpoint while forging the `shop-domain` header to any other tenant's domain, causing the handler to process attacker-controlled data as if it came from a different shop.

### Finding Description
`Webhooks::Request` builds its signable string from the raw body only: [1](#0-0) 

The `shop`, `topic`, `api_version`, and `webhook_id` accessors are read directly from HTTP headers and are never included in `to_signable_string`: [2](#0-1) 

`Registry.process` validates the HMAC (which only covers `@raw_body`) and then unconditionally trusts `request.shop`, `request.topic`, and `request.webhook_id` when constructing `WebhookMetadata` for the handler: [3](#0-2) 

The `HmacValidator` correctly checks `verifiable_query.hmac` against `HMAC(secret, to_signable_string)`: [4](#0-3) 

but since `to_signable_string` for a webhook request is just the raw body, this check proves only "this body byte-string was signed by someone holding `api_secret_key`" — it does **not** prove "this body belongs to shop X" or "this body is for topic Y". The documentation states this call "will verify the request did indeed come from Shopify," which is misleading given the `shop` field is unauthenticated: [5](#0-4) 

This is exactly the "shop authenticated versus shop stored/acted upon" binding break: the equality the code should enforce is `hmac-covered-shop == handler-consumed-shop`, but instead `hmac-covered-bytes == raw_body` while `handler-consumed-shop == unauthenticated header`. Any party that can generate one valid `(body, hmac)` pair for the app's secret — which happens routinely for a merchant who installs the app and triggers any webhook-eligible event on their own store — can replay that exact body to the app's public webhook endpoint with a different `shop-domain` header. The signature still validates (it only checks the body), and the handler will process/store the payload keyed to the attacker-chosen shop domain instead of the true origin shop.

### Impact Explanation
Any app built on this gem that keys persistence, authorization, or business logic in its webhook handler off `WebhookMetadata#shop` (the documented and expected pattern shown in the gem's own docs, e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) is exposed to cross-tenant data injection: an attacker-controlled shop can inject webhook bodies that get attributed to an arbitrary victim shop domain string. This crosses the tenant boundary the gem claims to enforce via `Registry.process`'s HMAC check, matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is elevated because the attacker doesn't need `api_secret_key` or any privileged credential — they only need to be a legitimate, unprivileged installer of the target app (any merchant can install most public apps) and can trigger an eligible webhook on their own store to obtain one valid `(raw_body, hmac)` pair signed by Shopify using the app's secret. They then replay that pair directly to the app's public webhook HTTP endpoint with a forged `shopify-shop-domain` header. No brute forcing or secret knowledge is required, and the gem's own `Registry.process`/`Request` code performs no cross-check tying the header-derived `shop` to the signed content.

### Recommendation
Bind the `shop`, `topic`, and `webhook_id` fields to the HMAC verification, or otherwise cryptographically tie them to the signed body, e.g.:
- Include the shop domain (and ideally topic/webhook id) in the string that is HMAC-verified, matching how `Oauth::AuthQuery#to_signable_string` includes `shop` in its signable payload.
- If Shopify's webhook HMAC scheme fundamentally only signs the body (as documented by Shopify), the gem should not present `process`/`validate_auth_callback`-style guarantees implying the shop header is verified; instead it should require callers to independently authenticate the origin (e.g., verify the registered webhook endpoint per shop, or cross-check `request.shop` against an expected/allow-listed shop before invoking the handler) and update the documentation in `docs/usage/webhooks.md` to make this limitation explicit so downstream apps don't trust `data.shop` without additional verification.

### Proof of Concept
1. App registers a webhook handler that stores incoming `data.body` keyed by `data.shop` (per the documented pattern in `docs/usage/webhooks.md`).
2. Attacker installs the app on `attacker-shop.myshopify.com` and performs an action that triggers a registered webhook topic (e.g. `orders/create`), causing Shopify to POST a body `B` with header `x-shopify-shop-domain: attacker-shop.myshopify.com` and a valid `x-shopify-hmac-sha256` computed over `B` using the app's `api_secret_key`.
3. Attacker's server (or a proxy they control) captures `(B, hmac)`.
4. Attacker sends a new HTTP request directly to the app's public webhook endpoint with the same raw body `B` and the same `hmac` header, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `HmacValidator.validate` succeeds because it only checks `HMAC(secret, B) == hmac`, which is unaffected by the header change: [6](#0-5) 
6. `Registry.process` invokes the handler with `shop: "victim-shop.myshopify.com"`, causing the app to attribute attacker-controlled data to the victim tenant. [7](#0-6)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
```

**File:** docs/usage/webhooks.md (L123-136)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

```ruby
class WebhookController < ApplicationController
  def webhook
    ShopifyAPI::Webhooks::Registry.process(
      ShopifyAPI::Webhooks::Request.new(raw_body: request.raw_post, headers: request.headers.to_h)
    )
    render json: {success: true}.to_json
  end
end
```
```
