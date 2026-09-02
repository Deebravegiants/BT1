### Title
Webhook `shop` identity is not bound to the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body, and `ShopifyAPI::Utils::HmacValidator.validate` only verifies that this raw body was signed with the app's shared secret. The `shop-domain` header, which `ShopifyAPI::Webhooks::Registry.process` uses as the tenant identity handed to app handlers, is never included in the signed payload. This is the same class of bug as M-7: a value that is later trusted and acted upon (`amountStored`/here, `shop`) is not the value that was actually verified (the truncated cast/here, the unsigned header), breaking the equality `verified_bytes == acted_upon_identity`.

### Finding Description
`AuthQuery#to_signable_string` correctly includes `shop` in the signed string, binding `shop` to the HMAC for OAuth callbacks: [1](#0-0) 

But `Webhooks::Request#to_signable_string` only returns `@raw_body`, while `shop` is read straight from an HTTP header that is entirely outside the signed material: [2](#0-1) 

`HmacValidator.validate` computes the signature purely over `to_signable_string` (the body) and compares it to the `hmac` header — it never touches `shop`: [3](#0-2) 

`Registry.process` then trusts the unauthenticated `request.shop` and forwards it directly to the app's handler as the tenant identity, alongside the body: [4](#0-3) 

Because every shop that installs the app shares the same `api_secret_key`, an attacker who controls their own (unprivileged) shop installation can legitimately trigger a webhook for their own store, capture the valid `(raw_body, hmac)` pair Shopify sent, and then replay that exact body+HMAC to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header for a victim shop. `HmacValidator.validate` will still succeed (it only checks the body against the shared secret), and `Registry.process` will hand the attacker-chosen `shop` value plus the attacker-controlled body to the app's webhook handler as if it came from the victim tenant. The library's own documentation states that `Registry.process` "will verify the request did indeed come from Shopify" — but it never asserts that the request came from the specific `shop` claimed in the header, so the property `authenticated_shop == acted_upon_shop` is not enforced: [5](#0-4) 

### Impact Explanation
This breaks the tenant/shop identity binding: the bytes that are cryptographically verified (`raw_body`) are decoupled from the identity (`shop`) that host applications use to route data, look up per-shop sessions, or write to per-shop storage. Any app that (reasonably, per the gem's own docs and `WebhookMetadata` design) trusts `data.shop` from `Registry.process` is exposed to cross-tenant data injection — an attacker-controlled shop can inject arbitrary webhook payloads attributed to a victim shop. This matches the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Exploitation requires only an unprivileged Shopify merchant account that installs the target app (a normal, unprivileged trust level for any public app), and the ability to trigger a webhook on their own store to obtain a valid `(body, hmac)` pair signed with the app's shared secret — no access to `api_secret_key`, access tokens, or other privileged material is needed. The replay itself is a simple HTTP POST to the app's public webhook endpoint with a modified header. This is a modest-but-real, credential-boundary-crossing likelihood.

### Recommendation
Bind the shop identity into the HMAC verification, not just the body. Options:
- Include the `shop-domain` (and ideally `topic`, `webhook-id`) header values in `to_signable_string`'s signed material context, if compatible with Shopify's outbound signing scheme, or
- Have `Registry.process` cross-check `request.shop` against an independently trusted source (e.g., the shop's active/known session or a per-shop registered webhook secret) before invoking handlers, rather than trusting the header value implicitly.
- At minimum, update `docs/usage/webhooks.md` to explicitly warn that `Registry.process`'s HMAC check does not authenticate the `shop-domain` header, and instruct implementers to independently validate that the shop is one they have an active session/install for before trusting the payload.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and registers/receives a webhook, capturing the exact `raw_body` (e.g. `{"id":1}`) and the corresponding `X-Shopify-Hmac-Sha256` value Shopify computed with the app's shared `api_secret_key`.
2. Attacker sends a POST to the app's webhook endpoint with:
   - `raw_body` = the captured body (unchanged, so the HMAC still validates)
   - `X-Shopify-Hmac-Sha256` = the captured, valid HMAC
   - `X-Shopify-Shop-Domain` = `victim-shop.myshopify.com` (spoofed)
   - `X-Shopify-Topic` = the topic registered for that handler
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate`, which succeeds because it only checks `raw_body` against the shared secret — it never inspects `shop-domain`.
4. `Registry.process` invokes the registered handler with `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body: ...)`, causing the app to process attacker-controlled data under the victim shop's identity.

### Citations

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
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
