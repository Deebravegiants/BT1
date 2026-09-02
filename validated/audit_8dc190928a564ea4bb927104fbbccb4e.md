### Title
Webhook shop-domain header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` signs only the raw request body, while `shop` is read from the unauthenticated `shopify-shop-domain` / `x-shopify-shop-domain` header. `ShopifyAPI::Webhooks::Registry.process` verifies the HMAC over the body only and then hands the header-derived `shop` straight to the app's webhook handler as an authenticated tenant identifier, breaking the intended binding `HMAC-covered bytes == identity attributed to the payload`.

### Finding Description
`Request#to_signable_string` returns `@raw_body` alone: [1](#0-0) 

`Request#shop` is parsed from a header that is not part of that signed string: [2](#0-1) 

`Registry.process` validates the HMAC (over the body only) and then forwards `request.shop` to the registered handler as the authenticated tenant identity: [3](#0-2) 

The gem's own documentation instructs integrators to treat `data.shop` as trusted, authenticated tenant identity ("The shop domain of the webhook") and use it directly for per-shop routing/side effects: [4](#0-3) 

Because the HMAC secret (`Context.api_secret_key`, the app's `client_secret`) is shared across all shops installing the same app, and only the body is signed, a valid `(body, hmac)` pair generated from a webhook fired by shop A remains valid when replayed with the `shop-domain` header swapped to shop B. `HmacValidator.validate` only recomputes the signature over `to_signable_string` (the body) and does the constant-time compare on that — the header value never enters the signed material: [5](#0-4) 

Equality that should hold and is broken: `shop_asserted_in_signed_bytes == shop_the_handler_acts_on`. Here the left side does not exist at all — nothing about `shop` is covered by the signature, yet the right side (`request.shop`, i.e., `data.shop` passed to the handler) is treated by documented usage as if it were authenticated.

### Impact Explanation
This is a cross-tenant identity-binding break carrying the app's own webhook trust boundary: an attacker who controls one shop (their own free/dev store, a legitimate install) can generate arbitrarily-bodied, validly-HMAC-signed webhook deliveries and then, since the shop-domain header is not covered by that signature, resend the same body+HMAC to the app's webhook endpoint claiming to be any other shop domain. Any app that follows the documented pattern (`data.shop`/`shop_domain` used to select the tenant record to update, per the shown docs example) will apply attacker-controlled webhook body content to a victim shop's data — i.e., cross-tenant data corruption/injection using only the attacker's own legitimately-issued webhook credentials, no access token or secret theft required.

### Likelihood Explanation
Exploitation only requires the attacker to operate one shop with the target app installed (trivial for public apps with free installs) and to be able to POST to the app's public webhook endpoint with modified headers — both are within reach of an "unprivileged internet user" as scoped by this analysis. The behaviour is deterministic and reproducible from the gem's code as shown, not a corner case.

### Recommendation
Include the shop domain (and ideally topic/api-version) in the signed material verified against Shopify's HMAC, or — since Shopify itself does not sign these headers — require/validate that `request.shop` matches a shop for which the app currently holds a registered webhook/session before invoking the handler, rather than passing the raw header value through as trusted identity. At minimum, document prominently that `data.shop` is unauthenticated and must be cross-checked against known installed shops before being used for any tenant-scoped effect.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and triggers any registered webhook topic (e.g. `orders/create`) with a body they control (e.g. by creating an order with attacker-chosen fields).
2. Shopify delivers the webhook to the app's endpoint with headers including a valid `x-shopify-hmac-sha256` (computed over the raw body using the app's shared `client_secret`) and `x-shopify-shop-domain: attacker.myshopify.com`.
3. Attacker captures this exact HTTP request (raw body + valid HMAC), then replays it to the same endpoint, changing only `x-shopify-shop-domain` to `victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses the forged header; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `to_signable_string` (`@raw_body`, unchanged) and succeeds, per `lib/shopify_api/webhooks/request.rb:35-38` and `lib/shopify_api/utils/hmac_validator.rb:26-31`.
5. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and the attacker-controlled body (`lib/shopify_api/webhooks/registry.rb:198`), and, following the documented pattern of using `data.shop`/`data.body` to update per-shop records, writes attacker-controlled data under the victim shop's tenant context.

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

**File:** docs/usage/webhooks.md (L12-30)
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
    end
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
