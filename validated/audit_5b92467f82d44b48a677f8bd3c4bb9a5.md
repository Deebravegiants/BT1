### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant shop-attribution via replay - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, but then hands the app's handler a `shop` value taken from the `x-shopify-shop-domain`/`shopify-shop-domain` header, which is never included in the signed material.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`ShopifyAPI::Utils::HmacValidator.validate` computes the HMAC purely from `to_signable_string`, i.e. the body, and compares it against the `hmac-sha256` header: [2](#0-1) 

`Registry.process` gates on that HMAC check, then immediately builds `WebhookMetadata` using `request.shop`, which is read straight from the unauthenticated `shop-domain` header: [3](#0-2) [4](#0-3) 

The identity binding the app relies on is: `hmac_valid(raw_body) == true` implies `shop_header == shop_that_generated_body`. That equality does not hold, because `shop` is excluded from `to_signable_string`. The `api_secret_key` used to sign webhooks is a single value shared across every shop that has the app installed (it is the app's client secret, not a per-shop key), so any merchant who installs the app can trigger a webhook for their own store and obtain a body+HMAC pair that is valid under the app's secret. That attacker-obtained `(raw_body, hmac)` pair can then be POSTed to the app's public webhook endpoint with the `shop-domain` header changed to a victim shop's domain. `Utils::HmacValidator.validate` will still return `true` because it only checks the body, so `Registry.process` will call the handler with `WebhookMetadata(shop: <victim's domain>, body: <attacker's own webhook body>)`.

As `docs/usage/webhooks.md` and `BREAKING_CHANGES_FOR_V15.md` show, this `shop` field is the value apps are expected to use to route/attribute the webhook payload to a tenant record (e.g. `perform_later(shop_domain: data.shop, webhook: data.body)`): [5](#0-4) 

Because the gem hands this unauthenticated field to the handler as if it were verified, any app that follows the documented pattern of trusting `data.shop` for tenant identification is exposed to cross-tenant data attribution.

### Impact Explanation
This breaks the tenant boundary the app relies on: an attacker who is merely an installer of the app on their own shop (no privileged Shopify credentials, no access to the app's `client_secret`, no access token) can make the gem report a self-generated webhook payload as belonging to a different, victim merchant. Depending on how the host app consumes `data.shop`, this can lead to cross-tenant data injection/attribution (e.g., an attacker-controlled order/customer payload processed under a victim shop's tenant identity), matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires only: (1) installing the app on an attacker-owned shop (a normal, permission-less action any merchant can perform to obtain a valid app installation and receive genuinely signed webhooks), (2) capturing one webhook body+HMAC pair from that shop, and (3) replaying it to the app's public webhook endpoint with a forged `shop-domain` header. No `api_secret_key`, access token, or other privileged credential is needed. This is a straightforward, repeatable replay against the gem's own documented `Registry.process` flow.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) header into the value that is HMAC-verified, or otherwise cryptographically tie the header set to the signed body — e.g. include the normalized `shop-domain`, `topic`, and `webhook-id` headers in `to_signable_string` before computing/comparing the signature, so that tampering with any of these headers invalidates the HMAC. At minimum, document/enforce that `Registry.process` must reject webhooks whose `shop` header does not match an expected/allow-listed shop for the topic, since `HmacValidator` currently offers no protection for that field.

### Proof of Concept
1. Install the target app on attacker-owned shop `attacker.myshopify.com`. Trigger any subscribed topic (e.g. `orders/create`) so Shopify sends a webhook to the app, legitimately signed with the app's shared `api_secret_key`:
   - Capture `raw_body` (e.g. `{"id":1,...}`) and the `x-shopify-hmac-sha256` header value.
2. Replay the captured request to the same app endpoint, but replace the `x-shopify-shop-domain` header with `victim-shop.myshopify.com`, leaving `raw_body` and the HMAC header untouched:
   ```
   POST /webhooks/callback HTTP/1.1
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <captured value>
   x-shopify-shop-domain: victim-shop.myshopify.com
   x-shopify-webhook-id: <any>
   x-shopify-api-version: 2024-01

   {"id":1,... attacker-controlled body ...}
   ```
3. `ShopifyAPI::Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb:189-200`) calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `raw_body` against the HMAC (`lib/shopify_api/webhooks/request.rb:35-38`, `lib/shopify_api/utils/hmac_validator.rb:26-31`).
4. The registered handler is invoked with `WebhookMetadata(shop: "victim-shop.myshopify.com", body: <attacker's payload>, ...)`, exactly as demonstrated by the gem's own test fixtures which construct `Request` from independently controllable headers and body (`test/webhooks/registry_test.rb:22-33`), confirming the header is never cross-checked against the signed content.

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
