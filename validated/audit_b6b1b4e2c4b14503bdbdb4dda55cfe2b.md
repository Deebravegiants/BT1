Confirmed: `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , meaning the `shop`, `topic`, `webhook_id`, and `api_version` headers are never included in the HMAC-signed material, yet `Registry.process` trusts `request.shop` unconditionally and forwards it to the app's handler as the tenant identity [2](#0-1) .

### Title
Webhook `shop` (and `topic`/`webhook_id`) headers are trusted without being covered by the HMAC signature, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the shop identity that is handed to the app's webhook handler entirely from the unauthenticated `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) header, while the HMAC signature that `Registry.process` validates only covers the raw request body.

### Finding Description
`Utils::HmacValidator.validate` verifies `verifiable_query.hmac` against `HMAC(secret, verifiable_query.to_signable_string)` [3](#0-2) . For webhook requests, `to_signable_string` is defined as simply the raw body:
```ruby
def to_signable_string
  @raw_body
end
``` [1](#0-0) 

The `shop`, `topic`, and `webhook_id` accessors are all read directly from HTTP headers that are not part of this signed string [4](#0-3) . `Registry.process` validates the HMAC of the body, then unconditionally trusts `request.shop`/`request.topic`/`request.webhook_id` and passes them straight into `WebhookMetadata` for the registered handler to act on [2](#0-1) . There is no cross-check that the shop in the header corresponds to a shop that legitimately owns the signed body, nor any binding between the `hmac` and the identity fields it is used to authorize.

The binding that should hold is: `HMAC-signed(body, shop, topic) == HMAC-signed(body) AND body/shop/topic used by handler`. Instead only `HMAC-signed(body) == HMAC-signed(body)` is checked, while `shop` (and `topic`/`webhook_id`) used by the handler are completely outside that check — a direct instance of "a field acted on but not covered by the HMAC."

Concretely: since `body`+`hmac` pairs are only ever produced together by Shopify for a specific, real webhook event tied to one shop, an attacker who operates their own store (a legitimate, unprivileged install of the target app) receives genuine `(body, hmac)` pairs for their own shop's events. They can replay that exact `(body, hmac)` pair to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain (and/or a different `topic`/`webhook-id`). `HmacValidator.validate` still succeeds because it only checks the (unchanged) body, so `Registry.process` calls the handler with `shop: "victim-shop.myshopify.com"` even though the body content actually originated from the attacker's own shop.

### Impact Explanation
This is a cross-tenant identity confusion: the app's webhook handler is told data belongs to a different merchant (`shop`) than the one that actually produced it. Any host application that uses `data.shop` from `WebhookMetadata` to select which merchant's records to create/update/delete (the exact documented usage pattern shown in `docs/usage/webhooks.md` — `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) can be tricked into attributing attacker-controlled webhook content to an arbitrary victim shop, or into processing mandatory compliance topics (e.g. `customers/redact`, `shop/redact`) against the wrong tenant. This matches the "cross-tenant access" Critical-impact category, since the tenant boundary (`shop`) enforced by the gem's own webhook verification API is bypassed using only a webhook payload the attacker already legitimately possesses for their own shop.

### Likelihood Explanation
Exploitation requires only: (1) the attacker be an app-installed merchant able to trigger any webhook topic for their own store (trivial, unprivileged), (2) network access to the app's public webhook endpoint (which is, by design, unauthenticated beyond this HMAC check), and (3) knowledge of the endpoint path (typically discoverable/documented). No access token, `client_secret`, or privileged credential is required — only a webhook capture that Shopify itself already sends the attacker for their own store.

### Recommendation
Include the identity-bearing headers (`shop`, `topic`, `webhook_id`, `api_version`) in the signed material that `HmacValidator` checks, or otherwise cryptographically bind them to the body before trusting `request.shop` in `Registry.process`. At minimum, document and/or enforce that consuming applications must independently verify `request.shop` corresponds to a shop with an active, registered session/install before acting on webhook data, since the current `to_signable_string` implementation for `Webhooks::Request` provides no such guarantee.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and triggers a real webhook event (e.g. updates a product to fire `products/update`).
2. Shopify delivers a legitimate request to the app's webhook endpoint with a valid `X-Shopify-Hmac-Sha256` header computed over the raw body using the app's `client_secret`.
3. Attacker intercepts/replays this exact `(raw_body, hmac)` pair to the same endpoint, but rewrites the `X-Shopify-Shop-Domain` header to `victim-shop.myshopify.com` (and optionally `X-Shopify-Webhook-Id`/`X-Shopify-Topic`).
4. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` and `ShopifyAPI::Webhooks::Registry.process` are invoked as shown in the documented Rails integration [5](#0-4) .
5. `Utils::HmacValidator.validate` returns `true` because it only re-hashes `raw_body`, which is unchanged [6](#0-5) .
6. The registered handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and the attacker-controlled body, and acts on it as if it were legitimate data for the victim shop.

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

**File:** docs/usage/webhooks.md (L128-135)
```markdown
class WebhookController < ApplicationController
  def webhook
    ShopifyAPI::Webhooks::Registry.process(
      ShopifyAPI::Webhooks::Request.new(raw_body: request.raw_post, headers: request.headers.to_h)
    )
    render json: {success: true}.to_json
  end
end
```
