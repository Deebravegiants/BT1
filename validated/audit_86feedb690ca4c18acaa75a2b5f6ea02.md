This confirms the finding: the docs explicitly instruct developers to trust `data.shop` (from `ShopifyAPI::Webhooks::Request#shop`, sourced from the `x-shopify-shop-domain`/`shopify-shop-domain` header) as the shop identity for the webhook, e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)` [1](#0-0) . But the HMAC signature computed by `HmacValidator` only covers the raw request body (`to_signable_string` returns `@raw_body`), never the shop-domain header [2](#0-1) [3](#0-2) .

`Registry.process` validates the HMAC over the body only, then builds `WebhookMetadata` using the unauthenticated `shop` header value taken directly from the request without any binding to the HMAC-verified content [4](#0-3) .

### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#hmac`/`#to_signable_string` binds only the raw webhook body to the signature, while the shop identity (`x-shopify-shop-domain` / `shopify-shop-domain` header) is read separately and is not part of the signed data. `ShopifyAPI::Webhooks::Registry.process` accepts the request as authentic once the body HMAC checks out, and then forwards the unauthenticated `shop` header value to the app's handler as the tenant identifier.

### Finding Description
`Utils::HmacValidator.validate` computes `OpenSSL::HMAC.hexdigest(sha256, secret, verifiable_query.to_signable_string)` and compares it to the received `hmac` [5](#0-4) . For webhook requests, `to_signable_string` is simply `@raw_body` [3](#0-2) , and `shop` is read straight from a header that is never fed into the signature computation [6](#0-5) .

`Registry.process` treats the request as verified purely based on body HMAC success, then constructs `WebhookMetadata` using `request.shop` (from the unauthenticated header) alongside `request.parsed_body` (the HMAC-verified body) [4](#0-3) . This breaks the equality that the gem's design implies: `hmac-verified identity == (body, shop)`, when it is actually only `hmac-verified identity == body`. The `shop` field acted upon by the host application is never covered by the HMAC.

Because Shopify signs webhooks for *all* shops of an app using the single shared `api_secret_key` (not a per-shop secret), any merchant who has installed the app can legitimately receive a validly HMAC-signed webhook body for their own shop (e.g., by placing an order to trigger `orders/create`). That merchant — an ordinary, unprivileged user of the app with no special credentials — can capture the raw body and its valid `x-shopify-hmac-sha256` value, then replay the same bytes to the app's webhook endpoint while swapping only the `x-shopify-shop-domain` header to a different shop's domain. Since the header is not covered by the signature, `HmacValidator.validate` still succeeds, and the app's handler executes attacker-controlled body content attributed to a shop the attacker does not control.

### Impact Explanation
This is a cross-tenant data-integrity/confusion issue: the gem hands the host application data that appears authenticated (HMAC passed) and tenant-scoped (`data.shop`), but the tenant binding is forgeable by any existing app merchant. Depending on how the host app uses `data.shop` (as documented, e.g., to route/store data per shop — `shop_domain: data.shop`), an attacker can inject fabricated webhook payloads (arbitrary JSON body of their choosing signed under their own shop) that get processed and stored/actioned under a victim shop's tenant, achieving cross-tenant data injection/corruption without ever compromising the victim or the app's `api_secret_key`.

### Likelihood Explanation
Likelihood is realistic: no special privileges beyond being a merchant who has installed the target app are required. The attacker only needs to capture one legitimate webhook (trivial, since they receive them for their own shop) and replay it with a modified HTTP header, which is fully within reach of an unprivileged internet-adjacent user.

### Recommendation
Bind the shop identity into the signed payload. Since Shopify's webhook signature scheme itself doesn't cover headers, the gem should not present `shop` (or other headers) as trusted/verified data. At minimum, the documentation and `WebhookMetadata` should make clear that only the body is authenticated by `HmacValidator.validate`, and any per-shop trust decision must additionally confirm the shop domain is one that is actually registered/expected (e.g., cross-checked against the app's known installed shops with a corresponding session) before acting on `data.shop`.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker-shop.myshopify.com`.
2. Attacker triggers an `orders/create` webhook (e.g., places a test order), causing Shopify to POST the event to the app's webhook endpoint with a valid `x-shopify-hmac-sha256` computed over the raw body using the app's `api_secret_key`.
3. Attacker intercepts/replays this exact raw body and HMAC header to the same endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` succeeds because it only checks the body against the HMAC.
5. `Registry.process` in `lib/shopify_api/webhooks/registry.rb` invokes the app's handler with `shop: "victim-shop.myshopify.com"` and the attacker-controlled body, even though this data never originated from `victim-shop`.

### Citations

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
