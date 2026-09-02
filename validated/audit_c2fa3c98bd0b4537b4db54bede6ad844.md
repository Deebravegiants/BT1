## Finding: Webhook `shop` (and topic/webhook-id) headers are not covered by the HMAC signature, enabling cross-tenant webhook spoofing

### Title
Webhook shop-domain header is trusted for tenant identity but is not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, while `Registry.process` uses the unauthenticated `shop-domain` header to identify the tenant for the webhook handler.

### Finding Description
`Utils::HmacValidator.validate` computes and compares an HMAC over `verifiable_query.to_signable_string` using `Context.api_secret_key`. [1](#0-0)  For webhooks, `to_signable_string` is defined to return only `@raw_body`: [2](#0-1) 

However, `Registry.process` derives the tenant identity passed to the app's handler from the `shop` accessor, which reads the `shopify-shop-domain`/`x-shopify-shop-domain` header — a value that is never part of the signed bytes: [3](#0-2) [4](#0-3) 

The identity-binding equality that is broken is:
`bytes verified by HMAC (raw_body)` ≠ `bytes acted on for tenant routing (shop-domain header)`.

Because the `api_secret_key` used to compute the webhook HMAC is the app's single client secret — the same key Shopify uses to sign webhooks for *every* shop that installs the app — any attacker who installs the target app on their own (attacker-controlled) shop legitimately receives real webhook deliveries with valid `body` + `hmac` pairs signed under that same shared secret. The attacker can then replay that exact `raw_body`/`hmac` pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` still succeeds (it only checks the body bytes), and `Registry.process` will invoke the handler with `WebhookMetadata.new(... shop: request.shop ...)` reporting the victim shop, per the documented handler contract shown in the gem's own usage docs (`shop:` is the field host apps are told to trust for tenant routing). [5](#0-4) [6](#0-5) 

### Impact Explanation
This allows an unprivileged attacker (any merchant who can install the target app on their own store) to inject arbitrary attacker-chosen webhook payloads that the app's handler will attribute to a different, victim tenant (shop) — a cross-tenant data-injection/spoofing vector, since the gem itself supplies `shop` as the trusted tenant discriminator to the handler despite it never being authenticated.

### Likelihood Explanation
Requires only: (1) the attacker to be an ordinary merchant with the app installed (or otherwise be able to capture one valid body/hmac pair, e.g. via a public webhook subscription the app registers on any shop), and (2) the ability to submit an HTTP POST to the app's known webhook endpoint with custom headers — both trivially available to any external, unauthenticated user of the app's webhook URL. No access token, `client_secret`, or privileged account is required.

### Recommendation
Include the `shop`, `topic`, and `webhook_id` header values in the signable payload/verification (or independently verify the `shop` domain against a session/tenant record before trusting it), so that the HMAC binds the tenant-identifying fields, not just the body.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com`; Shopify sends a real webhook: body `B`, header `x-shopify-hmac-sha256: H` (both computed with the app's shared `api_secret_key`), and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker replays the identical body `B` and `hmac H` to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate` passes because it only checks `B` against `H`. [1](#0-0) 
4. `Registry.process` calls the app handler with `shop: "victim-shop.myshopify.com"` and the attacker-controlled body, causing the host app to process/store forged data as if it originated from the victim shop. [4](#0-3)

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

**File:** docs/usage/webhooks.md (L10-27)
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
```
