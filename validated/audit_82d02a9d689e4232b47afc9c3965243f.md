## Title
Webhook shop/tenant identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, so `Utils::HmacValidator.validate` only proves that the body bytes were signed with the app's secret [1](#0-0) . The tenant-identifying `shop` field (and `topic`/`webhook_id`/`api_version`) is read straight from the `x-shopify-shop-domain` HTTP header, which is never included in the signed bytes [2](#0-1) . `Registry.process` accepts any request whose HMAC(body) matches, then dispatches the handler using this unauthenticated `shop` value as the tenant identity [3](#0-2) .

### Finding Description
This is the same class of bug as the CREATE2 report: an identity used to route/act on a request (the pool/pair address there, the tenant `shop` here) is computed/read from data that is disjoint from the data that was actually authenticated (the salt inputs there, the HMAC-signed bytes here). The equality that should hold and does not is:

`bytes_covered_by_HMAC ⊇ {shop, topic, webhook_id, api_version}` — but in fact `bytes_covered_by_HMAC = {raw_body}` only.

`HmacValidator.validate` calls `verifiable_query.to_signable_string`, and for `Webhooks::Request` that method returns just `@raw_body` [1](#0-0) . The `shop` accessor pulls from `shopify_header("shop-domain")`, which is not part of that signable string [2](#0-1) [4](#0-3) . `Registry.process` only checks `Utils::HmacValidator.validate(request)` (i.e., body-HMAC) before using `request.shop` to build `WebhookMetadata` and invoke the app's handler [3](#0-2) .

Any unprivileged internet user who can install the app on their own (free) development store is a legitimate webhook sender for that store — Shopify will produce a correctly HMAC-signed body for that attacker-controlled shop, using the app's real `client_secret`. Because the header carrying the tenant identity is outside the signed envelope, that same valid `(raw_body, hmac)` pair remains valid if the `x-shopify-shop-domain` header is swapped for an arbitrary victim shop domain before delivery to the app's webhook endpoint. The gem's own verification path (`Registry.process`) will accept it and hand the host application a `WebhookMetadata` claiming to be from the victim shop, even though the body/topic content was actually produced by (and signed for) the attacker's own store.

### Impact Explanation
Host applications built on this gem are documented to trust `WebhookMetadata#shop` for per-tenant data operations (e.g., "you have a session for a shop" webhook processing flow) [5](#0-4) . Because the gem's `process` API gives no cryptographic guarantee binding `shop` to the signed payload, an attacker who owns one shop can forge webhook events labeled as belonging to a different, victim tenant. Depending on how the host app uses `WebhookMetadata#shop` (e.g., to select which tenant's `access_token`/session/state to update or to trigger business logic scoped by shop), this can result in cross-tenant data corruption or cross-tenant action — one of the qualifying Critical impacts (cross-tenant access).

### Likelihood Explanation
Reachability requires only: (1) the attacker installs the app on their own store (this is the normal free/unprivileged onboarding flow for any Shopify app, requiring no leaked credentials, no access token, and no `api_secret_key`), and (2) the attacker is able to relay/replay the exact `(raw_body, hmac header)` pair they legitimately received to the app's public webhook endpoint while altering only the `x-shopify-shop-domain` header — a header entirely under the sender's control at the HTTP layer, and not part of what `HmacValidator` checks. No brute-forcing of the HMAC and no possession of the app's secret by the attacker is required, since Shopify computes the valid signature for the attacker's own legitimate webhook.

### Recommendation
Include the shop domain (and ideally topic/webhook id/api version) in the bytes that are HMAC-verified, or otherwise cryptographically bind them to the verified body (e.g., verify that the decoded body's own shop-identifying content matches the header, or require the host app to independently confirm `shop` against a known, previously-authenticated tenant such as a session lookup) before dispatching to handlers in `Registry.process`.

### Proof of Concept
1. Attacker registers a free/dev Shopify store `attacker-shop.myshopify.com` and installs the target app, subscribing (or letting Shopify auto-subscribe per app config) to a webhook topic.
2. Shopify sends `POST /webhook-endpoint` with headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: <topic>`, `x-shopify-hmac-sha256: <valid HMAC of raw_body computed with the app's real client_secret>`, and some raw JSON body.
3. Attacker intercepts/relays this exact request but rewrites only the `x-shopify-shop-domain` header to `victim-shop.myshopify.com`. `raw_body` and `x-shopify-hmac-sha256` are left untouched.
4. App's controller constructs `ShopifyAPI::Webhooks::Request.new(raw_body: ..., headers: ...)` and calls `ShopifyAPI::Webhooks::Registry.process(request)` [3](#0-2) .
5. `Utils::HmacValidator.validate(request)` returns `true` because it only checks `HMAC(raw_body)`, which is unchanged and still matches [6](#0-5) [1](#0-0) .
6. The app's registered handler is invoked with `WebhookMetadata` whose `shop` is `victim-shop.myshopify.com`, even though the payload originated from and was signed for `attacker-shop.myshopify.com` [7](#0-6) .

Note: exploitation ultimately depends on how the host application acts on `WebhookMetadata#shop`; I was unable to inspect `lib/shopify_api/webhooks/webhook_handler.rb` contents in this session (tool access limitation), so the exact downstream trust model of `handler.handle` in shipped apps could not be fully confirmed from the index alone — this is a gem-level identity-binding gap regardless.

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

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
