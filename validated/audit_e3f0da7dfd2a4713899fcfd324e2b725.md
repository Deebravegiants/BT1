### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, while the `shop` (and `topic`, `webhook_id`, `api_version`) values used by `ShopifyAPI::Webhooks::Registry.process` and handed to app handlers come from unauthenticated HTTP headers. An unprivileged party who is able to replay any single valid `(body, hmac)` pair can attach an arbitrary `x-shopify-shop-domain` header and have the gem report it as an authentic webhook for that shop, breaking the identity binding `shop delivered == shop that produced the signed body`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

but `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers with no cryptographic binding to the body or to the HMAC that is validated: [2](#0-1) 

`Registry.process` only checks the HMAC of `request` (i.e., of the body) before trusting every other field of the request, including `request.shop`, and forwards them unauthenticated into `WebhookMetadata`, which is passed to the app-provided handler: [3](#0-2) 

`HmacValidator.validate` in turn hashes only `verifiable_query.to_signable_string`, so anything outside that string (all four headers above) is unauthenticated for webhook requests, even though it's authenticated for `AuthQuery` (OAuth), where `shop` is part of `to_signable_string`: [4](#0-3) [5](#0-4) 

The gem's own documentation explicitly tells integrators to trust `data.shop` from the processed webhook as the tenant identifier for routing/queuing work: [6](#0-5) 

and the doc for `process` states it "will verify the request did indeed come from Shopify," implying the full request — including the shop — is authenticated, when only the body byte-string is: [7](#0-6) 

### Impact Explanation
This breaks the equality `shop authenticated by HMAC == shop acted upon by the handler`. In any deployment where the same webhook endpoint serves multiple shops (the normal multi-tenant SaaS pattern this gem is built for), an attacker who obtains one legitimate `(raw_body, hmac)` pair — e.g., from a webhook delivered to their own store/trial install, or a shop with predictable/public body content for a given topic — can POST it to the app's webhook endpoint with the `x-shopify-shop-domain` header set to a victim shop. `HmacValidator.validate` passes because the body/hmac pair is genuinely valid, and the handler receives `WebhookMetadata` claiming the data belongs to the victim shop. Depending on what the app does with `data.shop` (job enqueuing, cache keys, DB writes keyed by shop, etc.), this can corrupt or leak another tenant's data — a cross-tenant access issue.

### Likelihood Explanation
Exploitation requires only a single valid `(body, hmac)` sample for any topic/shop, which is not secret — no `api_secret_key`, access token, or privileged account is needed, and the webhook endpoint is a public, unauthenticated HTTP route by design. The attacker only needs to control HTTP headers on the request, which any unprivileged internet user can do.

### Recommendation
Include the authenticated identity fields (at minimum `shop`, and ideally `topic`/`webhook_id`) in the HMAC-signable content, or otherwise cryptographically bind them to the verified body (e.g., derive/verify shop identity from a source that is itself covered by the signature, matching the pattern already used for `AuthQuery#to_signable_string`). Until then, document loudly that `data.shop` from `ShopifyAPI::Webhooks::Registry.process` is unauthenticated and must not be trusted for tenant routing without independent verification (e.g., cross-checking against the shop for which the corresponding webhook subscription/ID was registered).

### Proof of Concept
```ruby
# Attacker captures one legitimate webhook delivery (body + valid hmac) for topic "orders/create",
# e.g. from their own dev store subscription.
raw_body = '{"id":1,"note":"hello"}'
valid_hmac = "<base64 hmac captured from a real Shopify delivery>"

# Attacker replays it, spoofing the shop-domain header to a victim shop.
spoofed_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => valid_hmac,
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # not covered by HMAC
  "x-shopify-webhook-id" => "attacker-controlled-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: spoofed_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate succeeds (hmac matches raw_body),
#    handler.handle receives WebhookMetadata(shop: "victim-shop.myshopify.com", ...)
#    even though that shop never sent/authorized this data.
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
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

**File:** docs/usage/webhooks.md (L123-125)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
