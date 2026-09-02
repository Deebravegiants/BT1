This confirms the finding: the docs explicitly state `Registry.process` "will verify the request did indeed come from Shopify" using the HMAC check, and downstream code trusts `data.shop` (from the unauthenticated `shop-domain` header) as the shop identity for dispatching business logic [1](#0-0) , while the actual signature only covers the raw body.

### Title
Webhook shop identity (`X-Shopify-Shop-Domain`) is not covered by HMAC verification, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `Utils::HmacValidator.validate` checks the HMAC solely against that body. The `shop` (and `topic`, `webhook_id`, `api_version`) values are read straight from HTTP headers that are never part of the signed payload, yet `Registry.process` forwards `request.shop` unchecked into `WebhookMetadata` as the authoritative tenant identity for the app's handler.

### Finding Description
`Request#hmac` and `Request#to_signable_string` are defined as: [2](#0-1) 

`shop` is pulled from the `shopify-shop-domain` header, which is not included in `to_signable_string`: [3](#0-2) 

`HmacValidator.validate` computes the signature purely from `to_signable_string` (the body): [4](#0-3) 

`Registry.process` validates only this body-bound HMAC, then trusts `request.shop` (and `request.topic`, `request.webhook_id`) as-is when constructing `WebhookMetadata`, which is handed directly to the app-supplied handler as the tenant/shop context: [5](#0-4) [6](#0-5) 

This is the exact bug class described in the external report: the security check (HMAC) validates one set of bytes (the body) while a different field that is acted upon downstream (`shop`) is not covered by that check — i.e. "the shop authenticated" (nothing, since shop isn't signed) versus "the shop the handler treats as the tenant of record" (`request.shop` from an attacker-controllable header) are not the same thing, breaking the identity binding `verified_shop == acted_upon_shop`.

Because Shopify's real webhook HMAC (which this library correctly mirrors) is computed only over the raw body, any legitimately-signed webhook body+HMAC pair (e.g., one an attacker receives for their own store, since any Shopify merchant can install an app and receive genuinely-signed webhooks for topics like `orders/create` with attacker-controlled order content) remains valid under `HmacValidator.validate` no matter what `X-Shopify-Shop-Domain` header value accompanies it. The gem provides no mechanism, hook, or documentation warning that `data.shop` must be independently corroborated (e.g., against a stored session/shop mapping) before being trusted as the tenant boundary.

### Impact Explanation
An attacker who is a legitimate merchant on their own shop can capture a genuinely Shopify-signed webhook body+HMAC (from any topic they can influence the content of, e.g. `orders/create`, `customers/create`) and replay it to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header rewritten to a victim shop domain. `Registry.process` will accept it as valid and hand the handler a `WebhookMetadata` claiming `shop: <victim-shop>` with attacker-controlled `body`. Any app that uses `data.shop` to select per-tenant state (session/access token lookup, tenant-scoped database writes, background job dispatch keyed by shop as shown in the gem's own docs example `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) will process attacker-controlled data under the identity of a different, unrelated merchant — a cross-tenant data injection/impersonation primitive rooted in this gem's verification boundary.

### Likelihood Explanation
Any developer following the gem's own documented usage pattern (dispatching per-shop background jobs keyed by `data.shop`) is exposed, since the gem exposes no signed/verified shop value and no warning that the header-derived `shop` is unauthenticated. The attacker only needs a store of their own (any developer/merchant account) capable of installing the target app and receiving one webhook — no access token, secret, or privileged account is required.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`) into the signed payload verified by `HmacValidator`, or require callers to cross-check `request.shop` against a shop value obtained through an independently authenticated channel (e.g., the shop tied to the currently loaded, verified session) before trusting it as tenant context. At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated header data and must not be used as a sole tenant-identity boundary.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and creates an order, triggering Shopify to deliver a genuinely-signed `orders/create` webhook: body `B`, header `X-Shopify-Hmac-Sha256: H` (valid HMAC over `B` using the app's real `client_secret`), header `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
2. Attacker replays this exact request to the app's webhook endpoint but rewrites the header to `X-Shopify-Shop-Domain: victim-shop.myshopify.com`, keeping body `B` and `X-Shopify-Hmac-Sha256: H` unchanged.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...shop-domain: "victim-shop.myshopify.com", hmac-sha256: H})` is constructed; `Utils::HmacValidator.validate(request)` succeeds because it only checks `H` against `B`, as in `lib/shopify_api/utils/hmac_validator.rb` and `lib/shopify_api/webhooks/request.rb`.
4. `Registry.process` invokes the app handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", body: B, ...)`, i.e. attacker-controlled order data processed under the victim shop's identity, breaking the intended `verified_shop == acted_upon_shop` binding.

### Citations

**File:** docs/usage/webhooks.md (L125-135)
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
