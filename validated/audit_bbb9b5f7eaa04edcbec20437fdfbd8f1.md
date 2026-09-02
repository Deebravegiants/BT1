### Title
Webhook shop-domain header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` signs and validates only the raw HTTP body via HMAC, while the `shop` (tenant identifier) is read directly from an unauthenticated HTTP header. Since Shopify apps use a single, app-wide `api_secret_key` shared across every shop that installs the app (there is no per-shop secret), any merchant who installs the app on their own store can obtain a validly-HMAC-signed `(body, hmac)` pair from a real webhook Shopify sends them, then replay that exact body/HMAC to the host application's webhook endpoint while forging the `X-Shopify-Shop-Domain` header to name a victim shop. The gem's `Registry.process` accepts this as authentic and hands the forged `shop` value to the application's handler as trusted tenant identity.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read directly from the `shopify-shop-domain` / `x-shopify-shop-domain` header, with no cryptographic binding to that value: [2](#0-1) [3](#0-2) 

`Registry.process` validates only the HMAC over the body via `HmacValidator.validate`, and then immediately trusts `request.shop` to construct `WebhookMetadata`, which is handed to the host application's handler as the authenticated tenant identifier: [4](#0-3) 

`HmacValidator.validate` computes the HMAC using the single `Context.api_secret_key` (or `old_api_secret_key`), which is the app's global secret — identical for every shop the app is installed on, not scoped per tenant: [5](#0-4) 

Because the HMAC only proves "this body was signed with the app's secret" and not "this body belongs to shop X", and because the secret is shared across every installation of the app, a low-privilege attacker who runs their own store with the target app installed can:
1. Receive a real webhook from Shopify for their own shop, capturing a valid `(raw_body, X-Shopify-Hmac-Sha256)` pair.
2. Replay that same body and HMAC header to the app's webhook endpoint, substituting `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `HmacValidator.validate` succeeds (body/HMAC pair is genuinely valid for the app's secret), and `Registry.process` calls the handler with `WebhookMetadata#shop == "victim-shop.myshopify.com"` even though the body/content actually originated from the attacker's own shop.

Per the docs, host applications are expected to use `data.shop` directly for tenant-scoped operations (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`), meaning the forged shop value flows straight into tenant-keyed logic: [6](#0-5) 

This is precisely the identity-binding failure called out by the rules: "a field acted on but not covered by the HMAC" — the `shop` field is acted upon (used to route/attribute the webhook) but is not part of `to_signable_string`, so it is never authenticated.

### Impact Explanation
This breaks the equality that should hold: `shop asserted by HMAC-authenticated payload == shop used as tenant key`. Instead, `shop` used as the tenant key comes from an unauthenticated header while the HMAC only authenticates the body content. An attacker with a legitimate (but unprivileged) installation of the app on their own store can inject arbitrary webhook data attributed to any other shop that has the app installed, causing the host application to process cross-tenant data as if it belonged to a victim merchant. Depending on how the host app uses webhook data (e.g., updating order/customer records, triggering fulfillment, mutating settings keyed by shop), this can result in cross-tenant data corruption or unauthorized actions performed under another merchant's identity — a cross-tenant access impact.

### Likelihood Explanation
Likelihood is high for any attacker capable of installing the target app on their own store (a normal, unprivileged capability for any Shopify merchant/developer using a public app), since no credentials beyond a legitimate installation are required, and the attack requires only standard HTTP replay tooling — no access to `api_secret_key`, access tokens, or the app's `client_secret`.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the signed content that `HmacValidator` verifies, rather than trusting it purely from an HTTP header. Concretely, have `Request#to_signable_string` incorporate the shop domain (e.g., verify the header value against a canonical representation covered by the HMAC, or require the host application to independently confirm the shop is a known, currently-installed tenant with an active session before processing) so that a body/HMAC pair signed for one shop cannot be replayed under another shop's identity.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com`.
2. Attacker triggers a real webhook event (e.g. `orders/create`) and captures the raw POST body and the `X-Shopify-Hmac-Sha256` header sent by Shopify — both are valid because they're computed with the app's shared `api_secret_key`, as shown in the test fixture pattern: [7](#0-6) 
3. Attacker replays a POST to the app's webhook endpoint with the identical `raw_body` and `X-Shopify-Hmac-Sha256`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `raw_body` against the HMAC: [8](#0-7) 
5. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and processes attacker-controlled data as if it came from the victim shop.

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

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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

**File:** test/webhooks/registry_test.rb (L16-28)
```ruby
        hmac = OpenSSL::HMAC.digest(
          OpenSSL::Digest.new("sha256"),
          ShopifyAPI::Context.api_secret_key,
          "{}",
        )

        @headers = {
          "x-shopify-topic" => @topic,
          "x-shopify-hmac-sha256" => Base64.encode64(hmac),
          "x-shopify-shop-domain" => @shop,
          "x-shopify-webhook-id" => "b1234-eefd-4c9e-9520-049845a02082",
          "x-shopify-api-version" => "2024-01",
        }
```
