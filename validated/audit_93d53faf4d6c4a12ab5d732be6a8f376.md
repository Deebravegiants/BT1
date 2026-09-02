Confirmed root cause. The webhook HMAC only signs the raw request body, and the `shop` value passed to the handler comes from an unsigned header — this is exactly the "field acted on but not covered by the HMAC" bug class.### Title
Webhook `shop` identity is taken from an unauthenticated header while the HMAC only covers the request body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by validating an HMAC computed over the raw request body, then hands the caller-supplied `shop-domain` header — which is never part of the signed material — to the app's webhook handler as the tenant identifier. Any request whose body/HMAC pair is valid (which an attacker can legitimately obtain for their own shop, since the same `client_secret` signs webhooks for every shop of the app) can be replayed with an arbitrary `shop-domain` header, causing the handler to process attacker-controlled body content as if it originated from a victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request` extracts `shop` from a header, independent of the signed payload: [1](#0-0) [2](#0-1) 

`to_signable_string` (used by `HmacValidator`) returns only `@raw_body`, so the `hmac-sha256` header — and consequently the equality it enforces — never binds `shop-domain`, `topic`, `webhook-id`, or `api-version` to the signature: [3](#0-2) 

`Registry.process` performs exactly that check and then immediately forwards `request.shop` — the unauthenticated header — to the app-provided handler as the tenant identity for the webhook event: [4](#0-3) 

The bound identity that the gem implicitly promises to the handler is:
`bytes verified by HMAC (raw_body)` == `bytes acted on (shop header used for tenant routing)`

That equality does not hold: the HMAC is computed only over the app's `client_secret` + raw body, a value that is shared across **every shop** that has installed the app. An unprivileged attacker who has installed the app on their own store (a normal, unprivileged action) can:
1. Trigger a webhook on their own shop (e.g. `orders/create`) with attacker-chosen resource content in the body.
2. Capture the genuine `x-shopify-hmac-sha256` value Shopify computed for that body (this is valid, since it is Shopify's own signature, not something the attacker forges).
3. Replay that exact `raw_body` + `hmac-sha256` header pair to the app's webhook endpoint, but swap `x-shopify-shop-domain` to the victim shop's domain (and optionally the topic/webhook-id headers, which are likewise unsigned).

`HmacValidator.validate` will pass because the signature check only covers `raw_body`, which is unchanged. `Registry.process` then calls the handler with `shop: request.shop`, i.e. the victim's domain, alongside attacker-controlled body content, header topic and webhook id: [5](#0-4) 

Any app built on this pattern (as documented) will persist/act on this data keyed by `data.shop`: [6](#0-5) 

### Impact Explanation
This breaks the tenant boundary the gem is expected to preserve for webhook delivery: an attacker who is merely an installer of the app on their own store can inject fabricated webhook events attributed to any other shop that has installed the same app, without possessing that shop's session, access token, or the app's `client_secret`. This is a cross-tenant data-integrity/confusion issue — the receiving app has no gem-provided means to distinguish a genuine victim-shop webhook from this forged one, since the identity field it relies on (`shop`) sits entirely outside the HMAC's protected scope.

### Likelihood Explanation
Likelihood is high for any app that has installed on at least one attacker-controlled shop (a normal precondition for third-party review/testing) and that has a public HTTP webhook endpoint reachable without additional authentication — which is the standard, documented deployment model for `ShopifyAPI::Webhooks::Registry`. No secrets beyond a standard app install are required.

### Recommendation
Bind `shop-domain` (and ideally `topic`/`webhook-id`) into the HMAC-signable material, or independently validate that the `shop-domain` header corresponds to a shop with an active, expected relationship to this specific webhook delivery (e.g. cross-check against the registered subscription/session store) rather than trusting the header as-is once the body-only HMAC passes.

### Proof of Concept
1. Install the target app on attacker-owned shop `attacker.myshopify.com`.
2. Trigger `orders/create` (or any subscribed topic) to receive a legitimate webhook POST with body `B` and header `x-shopify-hmac-sha256: H` (valid for `B` under the app's shared `client_secret`).
3. Replay to the app's webhook endpoint:
```
POST /callback/orders/create
x-shopify-topic: orders/create
x-shopify-hmac-sha256: H          # unchanged, still valid for body B
x-shopify-shop-domain: victim.myshopify.com   # forged
x-shopify-webhook-id: <any>

B
```
4. `ShopifyAPI::Utils::HmacValidator.validate` returns `true` (only `B` is checked). `ShopifyAPI::Webhooks::Registry.process` invokes the handler with `shop: "victim.myshopify.com"` and attacker-chosen `body: B`, even though `victim.myshopify.com` never sent this webhook.

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

**File:** docs/usage/webhooks.md (L12-26)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
```
