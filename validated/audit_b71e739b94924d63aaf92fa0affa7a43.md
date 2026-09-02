### Title
Webhook processing trusts the unauthenticated `X-Shopify-Shop-Domain` header while the HMAC only covers the raw body, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely via `Utils::HmacValidator.validate(request)`, which signs/verifies only the raw request body [1](#0-0) . It then trusts `request.shop`, which is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, a value that is never part of the signed material [2](#0-1) . The unverified `shop` value is passed straight into the handler as the tenant identifier [3](#0-2) .

### Finding Description
The HMAC secret used for webhook verification is the app's single `client_secret`, shared across every shop that has installed the app - it is not per-shop. `Registry.process` does:

```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))
end
``` [3](#0-2) 

`Utils::HmacValidator.validate` computes the signature only over `verifiable_query.to_signable_string`, and for `Webhooks::Request` that method returns just `@raw_body` [1](#0-0) , [4](#0-3) . None of `topic`, `shop`, `webhook_id`, or `api_version` - all read from headers via `shopify_header` - are covered by the signature [5](#0-4) .

Concretely, the identity-binding equality that should hold is:
`shop authenticated by HMAC == shop acted upon by the handler`

but the code actually enforces only:
`body authenticated by HMAC != shop header used by the handler`

The two are independent. Since the same `client_secret` is valid for HMACs generated for **any** shop on the app, an actor who legitimately controls one installed shop (an unprivileged multi-tenant peer, not requiring the app's leaked secret) can capture a real, validly-signed webhook body+HMAC pair for their own store, then replay it to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header changed to a different shop that also has the app installed. `HmacValidator.validate` still returns `true` because the body/HMAC pair is unmodified and valid for the shared secret, and `Registry.process` will invoke the handler with `data.shop` set to the attacker-chosen victim shop domain.

### Impact Explanation
This breaks the tenant boundary the SDK is documented to provide: app developers are told the `shop` field in `WebhookMetadata` is "The shop domain of the webhook" [6](#0-5)  and process webhooks by keying local records on `data.shop` (see the documented example calling `perform_later(topic: data.topic, shop_domain: data.shop, ...)`) [7](#0-6) . A host application following this documented pattern will write/mutate data under the wrong tenant's identity when fed a replayed, header-modified webhook, i.e. cross-tenant access/data corruption without needing the app's `client_secret`, access token, or any privileged credential.

### Likelihood Explanation
Likelihood is bounded by the following: an attacker must (a) obtain at least one valid raw-body + HMAC pair generated for the shared app secret (trivially available to any merchant that has installed the app, since Shopify sends them real webhooks), and (b) be able to POST an HTTP request to the app's public webhook endpoint with attacker-controlled headers (also trivial, since webhook endpoints are plain public HTTP(S) routes). No credentials, tokens, or TLS interception are required - this fits the "unprivileged internet user" threat model requested.

### Recommendation
Do not use the unauthenticated `shop` header as a trust boundary. At minimum:
- Document (and enforce in `Registry.process`) that the caller must independently verify `request.shop` against a shop that is actually known/registered for this app (e.g., cross-check against stored offline sessions) before acting on the webhook.
- Prefer binding the topic/shop/webhook-id into the material that's HMAC-validated, or reject processing when the shop header cannot be corroborated against an existing session for that shop.
- At minimum, surface a security note in `docs/usage/webhooks.md` warning that `data.shop`/`data.topic`/`data.webhook_id` are not covered by the Shopify HMAC and must not be trusted as tenant-scoping data by themselves.

### Proof of Concept
1. App has two shops installed: `shop-a.myshopify.com` (attacker-controlled) and `shop-b.myshopify.com` (victim).
2. Shopify sends a real webhook to the app for `shop-a`, e.g. `orders/create`, with body `{"id":1,...}` and headers including `x-shopify-hmac-sha256: <valid HMAC over body>` and `x-shopify-shop-domain: shop-a.myshopify.com`.
3. Attacker (who controls `shop-a` and can observe/replay their own webhook traffic, e.g. via a proxy) resends this exact body and HMAC to the app's webhook endpoint but changes the header to `x-shopify-shop-domain: shop-b.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` parses `shop` from the header [2](#0-1) .
5. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because the body/HMAC pair is untouched [8](#0-7) .
6. The registered handler is invoked with `WebhookMetadata.new(..., shop: "shop-b.myshopify.com", ...)`, causing the app to process order data belonging to `shop-a` as if it were `shop-b`'s data - a cross-tenant integrity violation.

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

**File:** docs/usage/webhooks.md (L12-14)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
```

**File:** docs/usage/webhooks.md (L19-29)
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
