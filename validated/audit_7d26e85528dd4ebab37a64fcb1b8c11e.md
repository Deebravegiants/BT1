Confirmed: this reproduces the exact "Analog Scan" bug class — a field acted on but not covered by the HMAC.

### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant data confusion via header spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` signs only the raw HTTP body [1](#0-0)  while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from unauthenticated HTTP headers [2](#0-1) . `Registry.process` validates the HMAC over that body-only string and then forwards `request.shop` verbatim to the app's handler, treating it as the authenticated tenant identity [3](#0-2) .

### Finding Description
The identity binding that should hold is:
`hmac_verified_bytes == bytes_that_determine_tenant_identity`

Here it does not: `HmacValidator.validate` only proves that `body` was HMAC-signed with the app's `api_secret_key` [4](#0-3) ; it says nothing about which shop sent it. The `shop` value that `Registry.process` hands to the app-supplied `WebhookHandler` as `WebhookMetadata#shop` comes from the `x-shopify-shop-domain` header, which is never part of `to_signable_string` and is therefore fully attacker-controllable independent of the signed body [5](#0-4) .

Since the app's `api_secret_key` is shared across every shop that installs the app, any unprivileged internet user who legitimately installs the app on their own (attacker-controlled) shop can trigger a real, correctly-HMAC-signed webhook (e.g. `orders/create`) containing attacker-chosen body content. They can then replay that exact `(body, hmac)` pair to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` still passes (body unchanged, same app secret), and `Registry.process` calls the handler with `shop: "victim-shop.myshopify.com"` and attacker-controlled `body`, even though the data never actually originated at the victim shop.

### Impact Explanation
This breaks the tenant boundary the library is documented to provide: apps are told to key persistence/business logic off `data.shop` from `WebhookMetadata` [6](#0-5) , trusting that this value is as authenticated as the payload. An attacker can inject arbitrary, attacker-chosen webhook data attributed to any shop domain of their choosing (not just their own), leading to cross-tenant data confusion/injection — records, notifications, or triggered actions written into another merchant's tenant using data the attacker fully controls. This matches the "cross-tenant access" Critical impact category.

### Likelihood Explanation
High/practical: the only prerequisite is installing the app on any Shopify dev/trial store (something any internet user can do), capturing one legitimate webhook (body + valid `hmac-sha256` header), and re-POSTing it to the same public callback endpoint with a modified shop-domain header — no access token, `client_secret`, or privileged account required.

### Recommendation
Bind the shop identity to the verified bytes: either include the shop domain (and topic/webhook id) in the HMAC-signable content, or require applications to cross-check `request.shop` against a shop that is actually known/registered (e.g. has an active session/webhook registration) before trusting it, rather than passing the raw header value straight into `WebhookMetadata`.

### Proof of Concept
```ruby
# Attacker installs the app on their own store "attacker-shop.myshopify.com"
# and receives a legitimate webhook:
raw_body = '{"malicious":"payload"}'
hmac = Base64.encode64(
  OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), APP_SECRET, raw_body)
) # produced by real Shopify delivery to attacker's own shop

# Attacker replays it to the app's public webhook endpoint,
# swapping only the shop-domain header:
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => hmac,          # still valid, body untouched
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged
  "x-shopify-webhook-id" => "spoofed-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) returns true (only body is checked)
# => handler.handle(data: WebhookMetadata(shop: "victim-shop.myshopify.com", body: {"malicious"=>"payload"}, ...))
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```
