This confirms the vulnerability: the docs explicitly tell app developers to trust `data.shop` as the tenant identifier (`shop_domain: data.shop`), and `ShopifyAPI::Webhooks::Registry.process` is documented as verifying "the request did indeed come from Shopify" — but the `shop` field is never actually covered by that verification.

### Title
Webhook shop-domain header is not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook's authenticity by HMAC-verifying only the raw request body, while the `shop` (tenant identity) is read from a separate, unsigned HTTP header and passed straight to the app's handler as the trusted tenant identifier.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `ShopifyAPI::Utils::HmacValidator.validate` computes/compares the HMAC using exactly that signable string [2](#0-1) . The `shop` accessor, however, is read independently from the `shopify-shop-domain`/`x-shopify-shop-domain` header and is never part of the signed material [3](#0-2) .

`Registry.process` only checks `Utils::HmacValidator.validate(request)` (i.e. body integrity) before forwarding `request.shop` unchanged to the handler as the tenant identity: `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...))` [4](#0-3) .

Because the HMAC secret (`Context.api_secret_key`) is identical for every shop that installs the app, any body/HMAC pair that is valid for one shop's webhook is also a valid HMAC for the exact same body when replayed with a different `shopify-shop-domain` header — the signature check cannot detect the substitution since the header isn't part of `to_signable_string`. The documentation explicitly instructs developers to trust `data.shop` as the tenant/shop identity after "verif[ying] the request did indeed come from Shopify" [5](#0-4) , and to route work using it, e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)` [6](#0-5) .

This breaks the intended identity binding: `verified-owner-of(body+HMAC) == shop-domain-claimed-in-header`. In reality, the HMAC only proves `body` was signed by the app's shared secret; it says nothing about which shop the body belongs to.

An unprivileged attacker who legitimately installs the target app on their own shop (a normal, unprivileged action available to any internet user for public/free apps) can trigger a real event to obtain one genuinely-signed `(body, hmac)` pair from Shopify, then replay that exact body/HMAC to the app's webhook endpoint while substituting the `shopify-shop-domain` header with a victim shop's domain. `Utils::HmacValidator.validate` still returns `true` (body unchanged, same shared secret), and the app's handler processes the payload as if it belongs to the victim shop — resulting in cross-tenant data or command injection into the victim's session/state, exactly matching the report's "field acted on but not covered by the HMAC" class of bug applied to the shop-identity binding instead of a numeric deviation check.

### Impact Explanation
This is a cross-tenant authentication/identity issue: any app built on this gem's documented `Registry.process` pattern trusts `data.shop` as the authenticated tenant after HMAC "verification," but that field can be forged by any user who can generate one legitimately-signed webhook body for their own shop. Depending on how the host app keys sessions/state off `data.shop`, this can lead to writing attacker-controlled webhook data into another merchant's records, triggering business logic under an incorrect tenant, or other cross-tenant confusion — a Critical-class cross-tenant access impact.

### Likelihood Explanation
Exploitation requires only: (1) installing the target app on an attacker-controlled shop to receive one genuine signed webhook (trivial and unprivileged for many app installation flows), and (2) replaying the captured body with a modified `shop-domain` header to the app's public webhook endpoint. No access to `api_secret_key`, tokens, or victim credentials is required. Likelihood is high wherever a host app relies on `data.shop` from this gem without independently re-verifying shop identity.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the HMAC-covered signable string, or otherwise cryptographically bind the claimed shop to the verified body — e.g. verify that Shopify's HMAC is computed over `shop + raw_body`, or independently confirm `request.shop` against a shop-specific secret/session established during OAuth for that shop, before invoking the handler in `ShopifyAPI::Webhooks::Registry.process`. At minimum, document prominently that `data.shop` is unauthenticated and must not be trusted for tenant selection without additional verification (e.g. checking it against an existing installed-shop record before processing).

### Proof of Concept
1. Attacker installs the target Shopify app on their own shop `attacker.myshopify.com` and triggers a webhook event (e.g. `orders/create`), capturing the raw POST body and its valid `x-shopify-hmac-sha256` value from Shopify.
2. Attacker replays this exact request to the app's public webhook endpoint, keeping the body and `x-shopify-hmac-sha256` unchanged, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `Utils::HmacValidator.validate` recomputes the HMAC solely over `raw_body` [1](#0-0)  and returns `true`, since the body and shared secret are unchanged.
4. `Registry.process` passes `request.shop` (`"victim.myshopify.com"`) straight into `WebhookMetadata` [7](#0-6) , and the app's handler processes attacker-supplied data under the victim's identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```

**File:** docs/usage/webhooks.md (L123-135)
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
