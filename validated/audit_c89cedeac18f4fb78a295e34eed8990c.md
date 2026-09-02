## Finding

### Title
Webhook `shop-domain` header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, but the `shop` (tenant) identity that is handed to the app's webhook handler is read from the unauthenticated `shopify-shop-domain` HTTP header. Any party who can obtain one validly-signed `(body, hmac)` pair for a given payload — trivially available to any developer with the app installed on their own test store — can resend that exact body with a forged `shop-domain` header and have it accepted as coming from an arbitrary other shop.

### Finding Description
`Utils::HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string`: [1](#0-0) 

For webhooks, `to_signable_string` returns only the raw body: [2](#0-1) 

The shop identity, however, is derived independently from the `shopify-shop-domain` (or `x-shopify-shop-domain`) header, which is never part of the signed material: [3](#0-2) 

`Registry.process` validates the HMAC (over the body only) and then forwards the header-derived, unauthenticated `shop` value straight into the handler's `WebhookMetadata`: [4](#0-3) 

The documented handler contract explicitly instructs apps to key their tenant-scoped logic (job dispatch, record lookups, data writes) off this `shop` field: [5](#0-4) 

This breaks the intended identity binding: `HMAC-verified bytes == tenant-attributed bytes`. In reality, `HMAC-verified bytes == raw_body` while `tenant attribution == shop-domain header`, and the two are never cryptographically tied together. Any webhook payload that is shop-independent (e.g., topics with an empty or generic body such as `{}`) yields an HMAC that is valid for every shop simultaneously, since the secret and body are the only inputs to the signature — the shop is irrelevant to the computed digest. An attacker who has the app installed on their own store (or otherwise captures one authentic webhook delivery) can capture that valid `(raw_body, hmac)` pair and replay it directly to the app's public webhook endpoint with the `shop-domain` header rewritten to any victim `myshopify.com` domain. `Registry.process` will accept it as authentic and dispatch it to the handler tagged with the attacker-chosen shop.

### Impact Explanation
This is a cross-tenant identity confusion at the gem's core webhook-authentication boundary: the artifact that proves authenticity (HMAC over body) is decoupled from the artifact that identifies the tenant (`shop-domain` header). Host applications built per this gem's documented contract will attribute forged/replayed events to shops they do not belong to, allowing an unprivileged actor to inject spoofed events (e.g., trigger reprocessing, cause data loss/overwrite, or spoof lifecycle events like uninstall/redact for a shop they don't control) under another merchant's identity — a cross-tenant access violation.

### Likelihood Explanation
Exploitability requires only: (1) the app's public webhook endpoint URL, which is fixed/known, and (2) one authentic `(raw_body, hmac)` pair, which any developer can obtain simply by installing the target app on their own development store and capturing the real webhook Shopify sends them. No `api_secret_key`, access token, or privileged access is required. For any topic whose payload doesn't vary meaningfully by shop, the same captured pair is universally replayable against arbitrary shop domains.

### Recommendation
Bind the shop identity into the authenticated signature material, or otherwise cryptographically tie the `shop-domain` header to the signed body — e.g., include the header value in `to_signable_string`, or independently verify that `request.shop` matches a shop with an active, previously-established session/webhook registration before dispatching to the handler. At minimum, document/enforce that consuming apps must not trust `WebhookMetadata#shop` for tenant attribution without separately confirming it against a known, registered shop.

### Proof of Concept
1. Install the target app on attacker-controlled store `attacker.myshopify.com`; capture a real webhook delivery with a shop-independent body, e.g. topic `app/uninstalled` with body `{}` and its valid `x-shopify-hmac-sha256` header (computed as `HMAC-SHA256(api_secret_key, "{}")`, per `lib/shopify_api/webhooks/registry.rb:16-20` test fixture logic).
2. Send a POST directly to the app's public webhook endpoint with:
   - body `{}` 
   - `x-shopify-hmac-sha256`: the captured valid signature
   - `x-shopify-topic`: `app/uninstalled`
   - `x-shopify-shop-domain`: `victim-shop.myshopify.com` (any shop, not the attacker's)
3. `ShopifyAPI::Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) validates the HMAC against the body only — it succeeds — and dispatches `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` to the app's handler, which per the documented contract acts on that shop's data/state.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

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

**File:** docs/usage/webhooks.md (L10-30)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

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
    end
  end
end
```
```
