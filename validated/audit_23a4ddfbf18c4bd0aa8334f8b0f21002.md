### Title
Webhook shop identity spoofing via HMAC that only covers the body, not the `shop-domain`/`topic`/`webhook-id` headers - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw body only, while `shop`, `topic`, `api_version`, and `webhook_id` are read from unauthenticated HTTP headers. `Registry.process` validates only the body's HMAC and then trusts these header-derived values to build `WebhookMetadata`, so any request with a validly-signed body can be relabeled as belonging to any other shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

But `shop`, `topic`, `api_version`, and `webhook_id` are all pulled straight from HTTP headers that are never part of the signed payload: [2](#0-1) 

`HmacValidator.validate` computes the HMAC purely from `to_signable_string` (the body) with the app's `api_secret_key`: [3](#0-2) 

`Registry.process` checks only this HMAC and then unconditionally trusts `request.shop` (the header) to build the metadata handed to the app's handler: [4](#0-3) 

The identity binding that should hold is: `shop-domain header == shop the signature actually authorizes`. Because the header is excluded from `to_signable_string`, this equality is never enforced — the gem only proves "this body was signed by Shopify for some shop using this app's secret," not "this body was signed for *this* `shop-domain`."

Since a single app's `api_secret_key`/webhook signing secret is shared across every shop that installs the app, any unprivileged merchant who installs the app receives legitimately-signed webhooks for their own shop. That merchant can capture a genuine `raw_body` + `x-shopify-hmac-sha256` pair from their own store's webhook delivery, then replay it to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` (and `topic`/`webhook-id`) headers with a victim shop's values. `HmacValidator.validate` still passes because it only checks the (unmodified) body signature, and `Registry.process` then dispatches to the handler with `shop: <victim shop>` while the body content is the attacker's own data.

### Impact Explanation
This breaks the tenant boundary the webhook mechanism is supposed to guarantee: an app relying on `WebhookMetadata#shop` (or the `Request#shop`/`#topic` accessors) to decide which merchant's session/data a webhook applies to can be made to attribute attacker-controlled webhook bodies to an arbitrary victim shop. Any host application that persists webhook payloads, triggers actions, or looks up a stored `Session` keyed by `request.shop` is exposed to cross-tenant data injection/corruption — satisfying the "cross-tenant access" Critical impact criterion.

### Likelihood Explanation
Any internet user who can install the app on their own shop (a normal, unprivileged flow — no leaked credentials, no access token theft, no TLS interception needed) can obtain a validly-signed webhook body/HMAC pair and replay it with forged headers directly to the app's public webhook callback endpoint. This requires no special access beyond being a regular app installer.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the signed payload verification — i.e., bind `to_signable_string` (or a separate check in `Registry.process`) to the authenticated identity, such as verifying the header-derived `shop` against a value that is cryptographically bound to the signature, not just the raw body. At minimum, document/require host apps to cross-check `request.shop` against an expected, already-authenticated shop before trusting webhook content, and consider incorporating headers into the HMAC computation to match Shopify's guidance for header-aware verification.

### Proof of Concept
```ruby
# Attacker owns "attacker-shop.myshopify.com" and has legitimately installed the app.
# Shopify sends a genuine, correctly-signed webhook to the attacker for their own shop:
raw_body = '{"id":1,"note":"attacker-controlled payload"}'
valid_hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), app_secret, raw_body)

# Attacker replays the same body+hmac to the app's public webhook endpoint,
# but swaps the shop-domain header to the victim's shop:
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(valid_hmac),
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged
  "x-shopify-webhook-id" => "forged-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate passes (body signature is valid),
#    handler.handle receives WebhookMetadata(shop: "victim-shop.myshopify.com", body: attacker payload)
```

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
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
