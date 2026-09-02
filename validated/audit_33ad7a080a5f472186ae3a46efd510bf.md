## Title
Webhook `shop` (and `topic`/`webhook_id`) identity is trusted from unauthenticated HTTP headers while only the raw body is HMAC-verified, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by verifying an HMAC over the raw request body. However, the `shop` (and `topic`, `webhook_id`, `api_version`) attributes that the handler uses to attribute the webhook to a specific merchant are read directly from HTTP headers that are never included in the HMAC computation. This breaks the identity binding: `bytes verified (raw body) != identity attributed (shop header)`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

and `shop`, `topic`, `webhook_id`, `api_version` are all pulled straight out of caller-supplied headers, none of which participate in the signature: [2](#0-1) 

`Registry.process` validates the request using `Utils::HmacValidator.validate(request)`, which only checks `OpenSSL.secure_compare(computed_signature, received_signature)` against `to_signable_string` (the body): [3](#0-2) [4](#0-3) 

After this "verification" passes, the library hands the header-derived, unauthenticated `request.shop` straight to the app's handler as `WebhookMetadata#shop`: [5](#0-4) 

The library's own documentation states that `Registry.process` "will verify the request did indeed come from Shopify," implying the whole payload — including shop attribution — is trustworthy, which is not the case for the `shop` field: [6](#0-5) 

This is structurally identical to the reported bug class: a field that is *acted on* (`shop`, used to route/attribute the event to a tenant) is not covered by the HMAC that is used to authenticate the request.

### Impact Explanation
An attacker who can produce one legitimately-HMAC-signed webhook body for the target app (e.g., by installing the app on their own store and capturing a real Shopify-delivered webhook, or via any topic that echoes attacker-controlled body content signed by Shopify) can replay that exact `(raw_body, hmac)` pair to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header value. `Utils::HmacValidator.validate` still returns `true` because it only checks the body/HMAC pair, and the handler receives `data.shop` set to the attacker-chosen domain. Any app logic that uses `data.shop` to look up per-tenant configuration, correlate/store data, or make trust decisions is subject to cross-tenant data confusion/injection — an unprivileged internet user can attribute webhook data to a shop they do not own, without needing the shop's access token or `client_secret`.

### Likelihood Explanation
Any external actor with network access to the app's webhook endpoint can attempt this once they possess (or can induce Shopify to send them) at least one validly-signed webhook body — trivial for an attacker who installs the target app on their own development store, since Shopify signs and delivers real webhooks to any installed app. Replaying that body with a forged shop-domain header requires no special privileges, credentials, or timing constraints, and the flaw is present on every call to `Registry.process`.

### Recommendation
Do not treat `request.shop` (or `topic`/`webhook_id`) as authenticated. Either:
- Include the relevant headers in the HMAC-signable string if the transport allows a mutually-agreed extended signing scheme, or
- Require the calling application to independently corroborate `data.shop` against a shop it already has an active/expected session for before trusting it, and clearly document that only the body content is authenticated by `HmacValidator`, not the shop/topic headers.
- At minimum, update `docs/usage/webhooks.md` to stop stating the request "did indeed come from Shopify" in a way that implies header integrity, and warn integrators that `data.shop` must be cross-checked before being used for tenant-scoped operations.

### Proof of Concept
1. Install the target app on attacker-owned store `attacker-shop.myshopify.com`; trigger any subscribed webhook topic (e.g. `orders/create`) so Shopify sends a validly HMAC-signed request to the app's webhook endpoint, with body `B` and header `X-Shopify-Hmac-Sha256: H` computed over `B` using the app's `api_secret_key`.
2. Capture `B` and `H`.
3. Send a new HTTP POST to the same webhook endpoint with body `B`, header `X-Shopify-Hmac-Sha256: H` (unchanged/still valid because body unchanged), but `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because `B`/`H` still match.
5. The handler is invoked with `WebhookMetadata#shop == "victim-shop.myshopify.com"`, even though `victim-shop` never sent this webhook, demonstrating cross-tenant attribution of attacker-controlled body content.

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

**File:** docs/usage/webhooks.md (L125-136)
```markdown
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
