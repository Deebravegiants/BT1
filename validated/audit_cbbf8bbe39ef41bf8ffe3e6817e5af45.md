This confirms the finding: the docs explicitly state `Registry.process` "will verify the request did indeed come from Shopify" (`docs/usage/webhooks.md:125`), and `data.shop` is documented as "The shop domain of the webhook" (`docs/usage/webhooks.md:14`), intended to be trustworthy for routing/attribution (e.g. `shop_domain: data.shop` in the example handler). But the HMAC only signs the raw body — the `shop` field is never covered by the signature.

### Title
Webhook `shop` field is not covered by HMAC verification, allowing tenant spoofing in `ShopifyAPI::Webhooks::Registry.process` - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body [1](#0-0) , and `HmacValidator.validate` verifies the HMAC exclusively against that signable string [2](#0-1) . The `shop` accessor, however, is read directly from the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` header [3](#0-2) , and that same unauthenticated value is what `Registry.process` forwards to the app's handler as the shop identity [4](#0-3) .

### Finding Description
The equality that should hold is: `shop_used_by_handler == shop_covered_by_HMAC`. In reality:
- `HmacValidator.validate(request)` only proves `HMAC(body, api_secret_key) == received_hmac` — it says nothing about which shop sent it.
- `request.shop` is parsed straight from the `shop-domain` header, which is not part of the signed bytes.
- `Registry.process` passes this unverified `request.shop` into `WebhookMetadata` and on to the app's `handler.handle` [4](#0-3) .

The gem's own documentation tells developers that `Registry.process` "will verify the request did indeed come from Shopify" [5](#0-4)  and that `data.shop` is "The shop domain of the webhook" [6](#0-5) , with the sample handler using it directly as a tenant key: `perform_later(topic: data.topic, shop_domain: data.shop, ...)` [7](#0-6) . This documented contract implies `data.shop` is as trustworthy as the HMAC-verified body, but it isn't bound to the signature at all.

An unprivileged internet user who can obtain any genuinely-signed webhook for *some* shop (trivially achievable by installing the public app on their own free/dev store and triggering an event) can replay that exact body+HMAC to the victim app's webhook endpoint while substituting an arbitrary value in the `shop-domain` header. `HmacValidator.validate` still returns `true` (the body and secret are unchanged), so `Registry.process` proceeds and calls the handler with `data.shop` set to the attacker-chosen value.

### Impact Explanation
This breaks the tenant-identity binding relied on by the documented integration pattern: apps that key per-shop state (session/access-token lookup, job routing, data attribution) off `data.shop` will attribute attacker-controlled webhook content to an arbitrary victim shop domain. Because `shopify_api`'s own documented session-storage pattern is to look up the stored `Auth::Session`/access token by shop domain, an app following the gem's guidance can be induced to process attacker payloads under another merchant's `shop` context — a cross-tenant confusion condition rooted entirely in this gem's failure to bind the `shop` field to the HMAC it verifies.

### Likelihood Explanation
Medium-to-high: no privileged credentials, access tokens, or `api_secret_key` are required — an attacker only needs their own legitimate app installation on any shop to obtain a validly-HMAC'd body, then can freely forge the `shop-domain` header on replay since it is never checked against the signature.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the HMAC-signed material, or independently verify that the `shop-domain` header corresponds to a shop with an active, known installation/session before trusting it in `WebhookMetadata`, rather than passing the raw unauthenticated header value straight to `handler.handle`.

### Proof of Concept
```ruby
# Attacker owns "attacker-shop.myshopify.com" with the target app installed,
# and captures a genuine webhook delivery (raw_body + x-shopify-hmac-sha256).
captured_body = '{"id":1,"note":"hi"}'
captured_hmac = "..."  # valid HMAC for captured_body under the real api_secret_key

forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => captured_hmac,   # unchanged, still valid for captured_body
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # spoofed, not covered by HMAC
  "x-shopify-webhook-id" => "forged-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: captured_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# HmacValidator.validate(request) => true (only checks captured_body)
# handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...))
# -> app processes attacker-controlled body under the victim shop's identity
```

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

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```

**File:** docs/usage/webhooks.md (L123-126)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

```
