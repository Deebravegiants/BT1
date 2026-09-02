### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable payload from the raw body only, while the `shop` (shop-domain) value that is later trusted as the tenant identifier for dispatching webhook data is taken from an HTTP header that is completely excluded from the signature.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`, and `Request#hmac` reads the signature from the `shopify-hmac-sha256`/`x-shopify-hmac-sha256` header: [1](#0-0) [2](#0-1) 

The `shop` accessor, however, is read from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is never mixed into `to_signable_string`: [3](#0-2) 

`Utils::HmacValidator.validate` verifies `verifiable_query.hmac` against `verifiable_query.to_signable_string` (the body) using `OpenSSL.secure_compare`, and never touches `shop`: [4](#0-3) 

`Webhooks::Registry.process` accepts any request whose body HMAC validates, then forwards `request.shop` directly into `WebhookMetadata` as the tenant identifier passed to the app's handler, with no cross-check that the HMAC-signed body actually corresponds to that shop: [5](#0-4) [6](#0-5) 

The identity binding that should hold is: `shop header used for tenant attribution == shop cryptographically bound into the signed payload`. In this gem, that equality does not hold — the HMAC binds only the raw body bytes, not the shop-domain header, so any request whose body+HMAC pair is valid (for *any* shop under the same app secret) can carry an arbitrary, attacker-chosen `shop-domain` header and still pass `HmacValidator.validate`.

This is documented behavior of the gem itself: the `docs/usage/webhooks.md` example simply forwards `data.shop` from the processed webhook as the tenant key (`shop_domain: data.shop`) after calling `Registry.process`, reinforcing that host apps are expected to trust `request.shop`/`data.shop` once the HMAC check passes — but the HMAC check provides no guarantee about that field. [7](#0-6) 

### Impact Explanation
An unprivileged attacker who is a legitimate (even free/dev-store) merchant using the target app can:
1. Trigger a genuine webhook from Shopify for their own store, obtaining a body `B` and a validly-signed HMAC over `B` (signed by Shopify using the app's real `client_secret`, which the attacker never needs to know).
2. Replay a crafted HTTP POST to the app's webhook endpoint with the same body `B` and HMAC, but with the `x-shopify-shop-domain` header rewritten to a victim shop's domain.
3. Because `HmacValidator.validate` only checks `B` against the HMAC and ignores the shop header, `Registry.process` accepts the request and hands the app's handler a `WebhookMetadata` claiming `shop: "victim-shop.myshopify.com"` while the body content actually belongs to the attacker's own store.

Any host application that keys per-tenant processing (data storage, billing, entitlement checks, queue routing) off `data.shop` — exactly as the gem's own documented example does — will attribute attacker-controlled data to the victim tenant, i.e. cross-tenant data injection/confusion. This satisfies the "cross-tenant access" High/Critical impact category, since it lets one tenant impersonate another tenant's identity through a channel the gem is meant to authenticate.

### Likelihood Explanation
The attacker only needs to be a legitimate app user (any merchant able to install the app on a store, including a free development store) and the ability to send arbitrary HTTP requests to the app's public webhook endpoint — no access to `api_secret_key`, access tokens, or the target shop's credentials is required. The vulnerable code path (`Request#to_signable_string`, `HmacValidator.validate`, `Registry.process`) is exercised on every processed webhook, so this is a structural gap in the library rather than a corner case.

### Recommendation
Bind the shop identity into the value that is cryptographically verified before it is trusted:
- Either include the `shop-domain` (and `topic`/`webhook_id`) header values in the signed payload used for `to_signable_string`, or
- Require the host application to cross-check `request.shop` against the shop associated with the specific webhook subscription/session that is expected to receive that topic, rather than trusting the header value implicitly once the body HMAC passes.
- Update `docs/usage/webhooks.md` to explicitly warn that `data.shop` is not covered by the HMAC and must not be used as the sole tenant key without additional verification.

### Proof of Concept
1. Merchant A installs the app on `attacker-shop.myshopify.com` and triggers a real webhook (e.g. `orders/create`) to the app's endpoint. Shopify sends body `B` with header `x-shopify-hmac-sha256: H` computed over `B` using the app's real secret, and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker replays the exact same request but changes only `x-shopify-shop-domain` to `victim-shop.myshopify.com`, keeping body `B` and header `H` unchanged.
3. Server calls:
   ```ruby
   ShopifyAPI::Webhooks::Registry.process(
     ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: { "x-shopify-hmac-sha256" => H, "x-shopify-shop-domain" => "victim-shop.myshopify.com", "x-shopify-topic" => "orders/create" })
   )
   ```
4. `HmacValidator.validate` returns `true` because it only checks `B` against `H`, per `lib/shopify_api/utils/hmac_validator.rb` lines 12-31 and `lib/shopify_api/webhooks/request.rb` lines 35-38.
5. The registered handler's `handle(data:)` is invoked with `data.shop == "victim-shop.myshopify.com"` and `data.body` derived from attacker-controlled `B`, per `lib/shopify_api/webhooks/registry.rb` lines 188-200 and `lib/shopify_api/webhooks/webhook_handler.rb` lines 6-12 — demonstrating the tenant-attribution bypass.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
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
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
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
