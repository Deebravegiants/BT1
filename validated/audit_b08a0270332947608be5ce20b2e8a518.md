### Title
Webhook HMAC Does Not Bind `shop-domain`, Allowing Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body [1](#0-0) , so `Utils::HmacValidator.validate` only proves that the *body bytes* were signed by Shopify with the app's shared `client_secret` [2](#0-1) . The `shop` field, which is read straight from the attacker-controllable `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header [3](#0-2) , is never part of the signed content, yet it is the value `Registry.process` hands to the app's handler as the tenant identifier [4](#0-3) .

### Finding Description
The identity binding that should hold is:
`shop asserted in the validated request == shop that produced/authorized the signed body`

`HmacValidator.validate_signature` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it to the `hmac` header [2](#0-1) . For `Webhooks::Request`, `to_signable_string` is defined as just `@raw_body` [1](#0-0) . The `shop`, `topic`, and `webhook-id` headers are parsed independently via `shopify_header` and are not folded into the signed string at all [5](#0-4) .

Because every shop installation of a given app shares the same `client_secret`, any body that was legitimately signed for shop A remains a validly-signed body when replayed verbatim with the `shop-domain` header changed to shop B — `Utils::HmacValidator.validate` still returns `true` because it never inspects the shop header. `Registry.process` then dispatches to the app's handler with `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)` [4](#0-3) , so the handler receives an attacker-chosen `shop` value paired with a genuinely-signed-but-foreign body.

The gem's own documentation instructs developers to key their downstream tenant logic directly off this unauthenticated field, e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)` [6](#0-5) , and explicitly claims that `Registry.process` "will verify the request did indeed come from Shopify" [7](#0-6)  — which is only true for the body, not for the shop attribution.

### Impact Explanation
An attacker who can obtain any one validly-signed webhook body for the target app (trivially available to them by installing the public app on their own store — a normal, unprivileged action) can replay that exact body with a forged `shop-domain` header naming a victim shop. The app's webhook pipeline will accept it as authentic and process it under the victim tenant's identity, since `Utils::HmacValidator.validate` and `Registry.process` never check that the signed body actually belongs to the shop asserted in the header. This is a cross-tenant data-integrity/access break: the app can be made to write, queue, or act on attacker-supplied (but genuinely Shopify-signed) data under another merchant's tenant context.

### Likelihood Explanation
High. No credentials, API tokens, or privileged access are required — only the ability to install the app on any shop (or replay a previously observed legitimate webhook) and forge the `shop-domain` header, which any client controls when POSTing to the app's webhook endpoint.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`) into the HMAC-signed content, or otherwise cryptographically verify that the shop the request claims to be from is consistent with the signing key/context before dispatching to the handler — mirroring the fix pattern requested in the report (ensure state-affecting identity fields are covered by the authenticity check, not just checked "for information").

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a legitimate webhook (e.g. `orders/create`), capturing the raw POST body and its `x-shopify-hmac-sha256` header — both validly signed with the app's shared `client_secret`.
2. Attacker POSTs the exact same body + `x-shopify-hmac-sha256` value to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` accepts the request (all required headers present) [8](#0-7) .
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only re-hashes `@raw_body` [9](#0-8) .
5. The handler is invoked with `WebhookMetadata` claiming `shop: "victim-shop.myshopify.com"` alongside the attacker's own webhook payload, letting the attacker inject/forge data attributed to the victim tenant.

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

**File:** lib/shopify_api/webhooks/request.rb (L45-63)
```ruby
      sig { params(raw_body: String, headers: T::Hash[String, T.untyped]).void }
      def initialize(raw_body:, headers:)
        # normalize the headers by forcing lowercase, removing any prepended "http"s, and changing underscores to dashes
        headers = headers.to_h { |k, v| [k.to_s.downcase.sub("http_", "").gsub("_", "-"), v] }

        missing_headers = []
        ["topic", "hmac-sha256", "shop-domain"].each do |name|
          unless headers.key?("shopify-#{name}") || headers.key?("x-shopify-#{name}")
            missing_headers << "shopify-#{name} or x-shopify-#{name}"
          end
        end
        unless missing_headers.empty?
          raise Errors::InvalidWebhookError,
            "Missing one or more of the required HTTP headers to process webhooks: #{missing_headers}"
        end

        @headers = headers
        @raw_body = raw_body
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L65-70)
```ruby
      private

      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```

**File:** docs/usage/webhooks.md (L123-125)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
