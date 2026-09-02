### Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) headers are trusted without HMAC coverage, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` claims to "verify the request did indeed come from Shopify," but the HMAC signature it validates only covers the raw request body. The `shop`, `topic`, `webhook_id`, and `api_version` values — all pulled straight from unauthenticated HTTP headers — are handed to the app's webhook handler as if they were verified, breaking the binding between "bytes verified" and "bytes/identity acted on."

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate_signature` computes and compares the HMAC exclusively against that signable string: [2](#0-1) 

Meanwhile, `Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are read directly from headers with no cryptographic binding to the HMAC at all: [3](#0-2) 

`Registry.process` verifies only the HMAC and then immediately trusts `request.shop` as the tenant identity passed to the app's handler: [4](#0-3) 

The documentation reinforces the false guarantee, stating that `Registry.process` "will verify the request did indeed come from Shopify" before invoking the handler with `data.shop`: [5](#0-4) 

Because the equality the gem is supposed to enforce is `shop used for tenant identity == shop cryptographically bound to the verified bytes`, and instead the actual check is only `hmac(raw_body) == received_hmac` with `shop` taken from an independent, unsigned header, an attacker who possesses **any** validly-signed webhook body/HMAC pair (trivially obtainable by installing the app on their own store, since they are a legitimate unprivileged merchant of their own shop) can replay that exact body+HMAC while substituting the `X-Shopify-Shop-Domain` header for a victim shop's domain. `HmacValidator.validate` still returns `true` because the body is byte-for-byte unchanged, and `Registry.process` calls the app's handler with `shop: "victim-shop.myshopify.com"` alongside attacker-controlled body content.

### Impact Explanation
If the host application uses `data.shop` from `WebhookMetadata` to scope any write, lookup, or business action (a standard and documented usage pattern — see the sample handler in `docs/usage/webhooks.md` calling `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`), the attacker can inject their own attacker-controlled webhook body into a victim shop's tenant context. This is a cross-tenant access primitive achieved without ever possessing the app's `client_secret` or the victim's access token — the attacker only needs a legitimately-issued webhook of their own to replay with a forged shop header. This satisfies the Critical impact bar (cross-tenant access) defined in scope.

### Likelihood Explanation
The attacker only needs to be an ordinary merchant who has installed the target app on their own (attacker-owned) shop — no privileged access, leaked secrets, or interception of Shopify-to-app traffic is required. Capturing a legitimate body+HMAC pair delivered to their own webhook endpoint and replaying it with a modified `shop-domain` header is straightforward, and the gem's own validation path (`Registry.process` / `HmacValidator.validate`) will accept it unconditionally since the header is not covered by the signature.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`/`api_version`) values into the HMAC-verified surface, or independently cross-check `request.shop` against the shop associated with the session/webhook subscription the app expects for that endpoint before trusting it as tenant identity. At minimum, update `VerifiableQuery#to_signable_string` for webhooks to incorporate the shop-domain header (matching Shopify's actual signing behavior only if such coverage exists) or require app-side re-validation of `data.shop` against known installed shops before use, and update `docs/usage/webhooks.md` to no longer imply that `Registry.process` authenticates the entire request including headers.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` (a normal, unprivileged installation).
2. Attacker triggers/receives a legitimate webhook (e.g., `orders/create`) to their own endpoint, capturing the raw body `B` and the valid `X-Shopify-Hmac-Sha256` header `H = HMAC-SHA256(client_secret, B)`.
3. Attacker sends a forged HTTP request to the app's webhook route with:
   - Body: `B` (unchanged)
   - `X-Shopify-Hmac-Sha256: H` (unchanged, still valid since body unchanged)
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (forged)
   - `X-Shopify-Topic`, `X-Shopify-Webhook-Id` left as attacker's own or forged as desired.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate`, which passes because it only checks `B` against `H`.
5. The app's handler is invoked with `WebhookMetadata(shop: "victim-shop.myshopify.com", body: B, ...)`, causing the host application to process attacker-controlled data as belonging to `victim-shop.myshopify.com`.

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
