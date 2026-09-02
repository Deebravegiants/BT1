### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, but the `shop` value that is handed to the app's handler as the tenant identifier is read from an HTTP header that is never included in the signed data. This breaks the equality that should hold between "the shop whose secret validated this request" and "the shop the application acts on behalf of."

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is instead read from the `shopify-shop-domain`/`x-shopify-shop-domain` header, completely independent of the signed payload: [2](#0-1) 

`Registry.process` verifies only the HMAC via `Utils::HmacValidator.validate(request)` and then forwards `request.shop` straight into `WebhookMetadata`, which is passed to the app-provided handler as the trusted tenant identifier: [3](#0-2) 

`HmacValidator.validate` computes the signature only from `verifiable_query.to_signable_string` (i.e., the body) and compares it against the header-supplied HMAC using `OpenSSL.secure_compare`: [4](#0-3) 

Because `api_secret_key` is a single, app-wide secret shared across every shop that installs the app (it is not a per-shop credential), any merchant who installs the app receives genuine, validly-signed webhooks from Shopify for their own store. That merchant can capture one such webhook (topic + raw body + valid HMAC) and replay the exact same body/HMAC pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. `HmacValidator.validate` will still pass, because the signature only covers the body, and `WebhookMetadata.shop` will report the victim shop even though the (attacker-controlled) body content never actually originated from, or was verified against, that shop.

This is the same identity-binding defect pattern as the analog bug class: a field (`shop`) that the application logic acts on (tenant identification, used by the handler for record association, e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)` per `docs/usage/webhooks.md`) is not covered by the value that authenticates the request (the body-only HMAC). [5](#0-4) 

### Impact Explanation
An attacker who is any legitimate (even free-tier) installer of the multi-tenant app can forge webhook deliveries that the host application will attribute to an arbitrary other tenant (`shop` value), while fully controlling the body content of that "genuine" webhook (by triggering an event in their own store with attacker-chosen field values, e.g., order notes, product titles, customer fields). Downstream, if the host app uses `data.shop` to decide which tenant record to update/create (a common pattern, as shown in the gem's own documentation example), this results in cross-tenant data injection/corruption without ever needing the app's `client_secret` or any tenant's access token — satisfying the Critical "cross-tenant access" impact bar.

### Likelihood Explanation
Requires only that the attacker be an ordinary, unprivileged installer of the target app (no special privileges, no leaked secrets) and be able to trigger a webhook-eligible event in their own store, then replay the captured request to the app's public webhook endpoint with a modified shop-domain header. This is straightforward to script and does not require breaking cryptography, since the shop header sits entirely outside the HMAC's scope.

### Recommendation
Do not trust the `shop` header value for any authorization, tenant-scoping, or data-association decisions unless the shop is cross-checked against an established, authenticated relationship (e.g., verify that the `shop` header value corresponds to a shop domain that has an active, registered webhook/session in your own tenant database, and reject if the resulting shop was not the one that actually registered for that topic/webhook id). More robust: extend `to_signable_string` (or webhook processing) to include the shop-domain header in what is authenticated, or validate `webhook_id`/topic against a per-shop registration record before trusting `data.shop`.

### Proof of Concept
1. Attacker signs up as a normal merchant and installs the vulnerable app on `attacker-shop.myshopify.com`, subscribing it to `orders/create`.
2. Attacker creates an order in their own store with attacker-chosen field values, causing Shopify to deliver a genuinely HMAC-signed webhook to the app's endpoint:
   - Headers: `X-Shopify-Hmac-Sha256: <valid signature over body>`, `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Topic: orders/create`.
3. Attacker captures this raw request (body + valid HMAC signature) via a local proxy.
4. Attacker resends the identical body and `X-Shopify-Hmac-Sha256` value to the same app endpoint, but replaces the header with `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `Utils::HmacValidator.validate` passes because it only checks the body signature (`request.rb:35-38`, `hmac_validator.rb:26-31`).
6. `Registry.process` invokes the app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker-controlled body>, ...)` (`registry.rb:198-199`), causing the host application to process attacker-controlled data as if it belonged to `victim-shop`.

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

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```
