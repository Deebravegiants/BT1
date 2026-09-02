Confirmed: `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are all read directly from HTTP headers with no HMAC coverage [2](#0-1) . `Registry.process` validates only this body-only HMAC and then forwards `request.shop` (the unauthenticated header value) straight to the app's handler as the tenant identifier [3](#0-2) .

### Title
Webhook `shop`/`topic`/`webhook_id` headers are not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its verifiable signature over the raw body only. The `shop-domain`, `topic`, `webhook-id`, and `api-version` values are parsed straight from HTTP headers and are never included in the signed payload, yet `Registry.process` passes `request.shop` on to the app's webhook handler as the authoritative tenant identifier after HMAC validation succeeds.

### Finding Description
`Request#to_signable_string` is defined as simply `@raw_body` [1](#0-0) . `HmacValidator.validate` computes the HMAC exclusively over `verifiable_query.to_signable_string` and compares it to the `hmac` header value [4](#0-3) . The `shop`, `topic`, `webhook_id`, and `api_version` accessors all read from `@headers`, which are attacker-controllable HTTP headers on the incoming request, not from anything cryptographically bound to the body [2](#0-1) .

`Registry.process` validates the HMAC (over body only) and then constructs `WebhookMetadata` using `request.shop` — the unverified header — as the tenant identity passed to the app's handler [3](#0-2) . The documented usage pattern explicitly relies on `data.shop` to route/attribute webhook data per tenant (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`), confirming that host apps are expected to trust this field as the shop that generated the webhook [5](#0-4) .

The identity binding broken here is: `shop (that produced/authorized the signed body)` == `shop (delivered to the handler as request.shop)`. Because the header is outside the HMAC's scope, these two values can diverge for any attacker who possesses one valid `(body, hmac)` pair signed with the app's real secret — which happens routinely for any merchant who installs the app on their own store and receives a legitimate webhook delivery. That merchant can capture their own valid webhook body+HMAC and replay it to the app's public webhook endpoint with the `shop-domain` (and/or `topic`/`webhook_id`) header rewritten to name a different, victim shop. `Registry.process` will accept it as valid (the HMAC still matches the untouched body) and hand the handler `data.shop == "victim-shop.myshopify.com"` with attacker-chosen body content — a cross-tenant data injection into the victim's context in the host application.

### Impact Explanation
This breaks the shop-to-webhook binding relied upon by every documented multi-tenant handler pattern in this gem's own docs. A merchant of the app (an "unprivileged internet user" from the perspective of other tenants) can inject arbitrary attacker-chosen webhook payloads that are attributed to a different, unrelated shop in the host application — a cross-tenant access/data-poisoning primitive, since the receiving app has no cryptographic assurance that the `shop` header matches the shop whose secret actually produced the body.

### Likelihood Explanation
Exploitation only requires the attacker to install the target app on any shop they control (a normal, unprivileged action), capture one legitimate webhook delivery (body + `x-shopify-hmac-sha256`), and replay it to the app's public webhook endpoint with a modified `shop-domain` (and optionally `topic`/`webhook-id`) header. No access to the app's `client_secret`, no privileged account, and no interception of another tenant's traffic is required.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the HMAC-signed payload (or otherwise cryptographically bind them, e.g. by deriving them only from a value verified against the shop's own registered installation/session rather than trusting the header), and have `Registry.process` cross-check `request.shop` against the shop associated with the webhook subscription/session before dispatching to the handler.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` and registers the `orders/create` webhook.
2. Shopify delivers a legitimate webhook: body `B`, header `x-shopify-hmac-sha256: H` (valid for `B` under the app's real secret), `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker replays this exact `(B, H)` to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Utils::HmacValidator.validate` succeeds because it only checks `B` against `H` [4](#0-3) .
5. `Registry.process` calls the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: B, ...)` [6](#0-5) , causing the host app to process attacker-controlled data under the victim shop's identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** docs/usage/webhooks.md (L19-30)
```markdown
```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```
```
