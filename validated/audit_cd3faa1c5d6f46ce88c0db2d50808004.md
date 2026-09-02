### Title
Webhook shop attribution is not covered by HMAC verification, allowing cross-tenant shop spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so the HMAC verification performed by `Utils::HmacValidator.validate` binds solely to the request body and never covers the `shop-domain` header. Since `Registry.process` reads the attributed tenant from `request.shop` (which comes exclusively from that unsigned header) while trusting the HMAC as proof of Shopify origin, an attacker holding any valid `(body, hmac)` pair from their own dev-shop webhook can replay it with a forged `x-shopify-shop-domain` header and have the app process it as belonging to an arbitrary victim shop.

### Finding Description
The broken binding is: `hmac_signed_bytes == bytes_the_handler_trusts_as_shop`. This is false because:

- `to_signable_string` returns `@raw_body` only, never `@headers`: [1](#0-0) 
- `shop` is read purely from the `shop-domain` header, independent of the signed body: [2](#0-1) 
- `HmacValidator.validate_signature` computes the HMAC over `verifiable_query.to_signable_string` (i.e., the body) and compares it to the header-supplied `hmac`, never touching the shop header: [3](#0-2) 
- `Registry.process` gates on that body-only HMAC check and then constructs `WebhookMetadata` using `request.shop` taken straight from the unsigned header, passing it to the app's handler as trusted tenant identity: [4](#0-3) 

Exploit flow: the attacker installs the target app on their own dev shop `attacker.myshopify.com`, triggers a real webhook (e.g. by creating an order with attacker-influenced fields), and captures the genuine `(raw_body, x-shopify-hmac-sha256)` pair Shopify computed using the app's shared `api_secret_key` (the same secret is used for every shop installing this app, not per-shop). The attacker then POSTs directly to the app's public webhook endpoint with the identical body and HMAC, but substitutes `x-shopify-shop-domain: victim-shop.myshopify.com`. `HmacValidator.validate` still passes because it only checks the body against the HMAC, and `Registry.process` invokes the app's handler with `WebhookMetadata#shop == "victim-shop.myshopify.com"`, causing the app to attribute attacker-controlled payload/content to the victim tenant.

No other guard intervenes: `ShopValidator.sanitize!`, the OAuth `state` check, `JwtPayload`'s `aud` check, and `Context.setup?/private?/embedded?` are unrelated to webhook processing; nothing in `Registry.process` or `Request` cross-checks the `shop-domain` header against the HMAC-signed content or against a known/installed shop for the given webhook_id.

### Impact Explanation
Any handler logic that keys off `WebhookMetadata#shop` (e.g., looking up the victim's stored session/access token to act on "their" event, writing attacker-supplied body content into per-shop records, enqueuing jobs scoped to `data.shop`) can be tricked into treating attacker-controlled content as originating from the victim tenant, as documented in the gem's own webhook usage guide advising handlers to key work off `data.shop`: [5](#0-4) . This is repeatable against arbitrary victim shops that have installed the same app, since the attacker only needs one legitimately-signed webhook of their own (the signing secret is shared across all shops on the app) and can swap the shop header freely per request. This is a cross-tenant impact: attacker-influenced data crosses a tenant boundary and is attributed to a shop the attacker does not control.

### Likelihood Explanation
Preconditions are modest and attacker-achievable without any privileged credentials: the app must have a registered `:http` webhook handler via `Registry.add_registration`, the victim shop must have installed the app (any installed shop qualifies, real identity unimportant to the attacker), and the attacker must independently install the same app on their own dev shop to receive a genuinely signed webhook. No `api_secret_key`, access token, or session is ever needed by the attacker — they only need to observe one webhook delivery to themselves and control HTTP headers on their own subsequent request. This is cheap, deterministic, and repeatable per victim shop domain.

### Recommendation
Bind the trusted shop identity to the HMAC-verified payload rather than to an independent, unsigned header. Concretely: incorporate the `shop-domain` (and ideally `webhook-id`/`topic`) into the signable string used for HMAC verification, or cross-validate `request.shop` against an app-maintained authoritative record (e.g., confirm a session/install exists for that shop and that the `webhook_id` was actually registered for it) before invoking the handler in `Registry.process`.

### Proof of Concept
Add a minitest (WebMock not required since no live shop) under `test/webhooks/` that:
1. Builds `body = '{}'` and computes `valid_hmac = OpenSSL::HMAC.hexdigest("sha256", ShopifyAPI::Context.api_secret_key, body)` (base64-encoded to match `Request#hmac`'s decode step), simulating a legitimately-issued webhook to the attacker's own shop.
2. Constructs `request_a = ShopifyAPI::Webhooks::Request.new(raw_body: body, headers: {"x-shopify-hmac-sha256" => valid_hmac_b64, "x-shopify-topic" => "orders/create", "x-shopify-shop-domain" => "attacker.myshopify.com"})` and `request_b` identical except `"x-shopify-shop-domain" => "victim-shop.myshopify.com"`.
3. Asserts `ShopifyAPI::Utils::HmacValidator.validate(request_a) == true` and `ShopifyAPI::Utils::HmacValidator.validate(request_b) == true` — both pass despite different shop attribution, proving the equality `hmac_signed_bytes == bytes_the_handler_trusts_as_shop` is false.
4. Registers a stub handler via `Registry.add_registration`, calls `Registry.process(request_b)`, and asserts the handler receives `WebhookMetadata#shop == "victim-shop.myshopify.com"` even though the HMAC was computed for the attacker's own body, demonstrating the cross-tenant attribution bypass end-to-end.

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
