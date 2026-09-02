### Title
Webhook HMAC only covers the request body, allowing shop/topic header forgery and cross-tenant webhook impersonation - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats an incoming webhook as fully authenticated once `Utils::HmacValidator.validate(request)` succeeds. However, that HMAC is computed only over the raw request body via `Request#to_signable_string`, which returns `@raw_body` and nothing else. The `shop`, `topic`, `api_version`, and `webhook_id` values that are subsequently trusted and handed to the app's `WebhookHandler` are read straight from HTTP headers that are never part of the signed bytes. This breaks the invariant that should hold for any "verified" webhook: `hmac_signed_bytes == identity_bound_tuple(shop, topic, webhook_id, api_version, body)`. In this gem, the equality actually enforced is only `hmac_signed_bytes == body`, so the shop/topic attribution is unauthenticated.

### Finding Description
The signable string for a webhook request is defined as: [1](#0-0) 

while `shop`, `topic`, `api_version`, and `webhook_id` are all pulled from headers via `shopify_header`, none of which participate in the HMAC computation: [2](#0-1) [3](#0-2) 

`Registry.process` validates the HMAC and then immediately trusts these header-derived fields to construct the metadata passed to the app's handler: [4](#0-3) 

`HmacValidator.validate`/`validate_signature` only ever compare against `verifiable_query.to_signable_string`, so for a `Webhooks::Request` object the check is body-only: [5](#0-4) 

Crucially, the `api_secret_key` used to compute this HMAC is the **app's** client secret, shared across every shop that installs the app — it is not shop-specific. This means a valid `(raw_body, hmac)` pair obtained from any legitimate webhook delivery (e.g. one delivered to the attacker's own shop after installing the app) is a valid HMAC for that same body regardless of which shop or topic header accompanies it. An attacker with a legitimate webhook delivery can therefore swap the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`, `x-shopify-api-version`) headers and resubmit the request to the app's webhook endpoint; `Utils::HmacValidator.validate` still returns `true` because it never inspected those headers, and `Registry.process` builds a `WebhookMetadata` object that misattributes the (still-valid, still-verified) body to an arbitrary victim shop/topic.

The gem's own documentation confirms that host apps are expected to trust `data.shop` directly from this verified metadata for downstream processing: [6](#0-5) 

So an app built exactly as documented (e.g., enqueuing background jobs keyed by `data.shop`) will process attacker-controlled shop attribution as if it were Shopify-verified.

### Impact Explanation
This breaks the "shop authenticated versus shop trusted downstream" binding described in the rules. Any party capable of triggering or capturing one legitimate webhook delivery for the app (e.g., a shop owner who installs the app, which requires no special privilege beyond normal use) can forge the shop/topic attribution of that verified payload and have the app process it as originating from a different tenant. Depending on how the host app uses `data.shop` (as documented: to key background jobs, look up sessions, or write data), this enables cross-tenant data confusion/injection — writing or triggering shop-A-controlled webhook bodies under shop B's identity, or replaying a topic as a different, unregistered/mandatory topic (`shop/redact`, `customers/redact`, `customers/data_request`) against an arbitrary shop. This matches the Critical "cross-tenant access" impact category, since the gem itself provides no mechanism to bind the verified body to the shop/topic it claims to represent.

### Likelihood Explanation
Likelihood is high for any app that has at least one active installation: the attacker needs no secrets, tokens, or elevated access — only a single genuine webhook delivery (which every installed merchant receives as part of normal use) and the ability to POST a modified HTTP request to the app's public webhook endpoint with different headers but the same body/HMAC. No cryptographic material needs to be broken; the vulnerability is a scope-of-signing gap, not a cryptographic weakness.

### Recommendation
Include the identity-critical headers (`shop-domain`, `topic`, and ideally `webhook_id`/`api_version`) in the HMAC-signed material, or otherwise cryptographically bind them to the body before trusting them in `Registry.process`. Since Shopify's own webhook signature only covers the body by protocol design, the mitigation belongs in this gem: reject/ignore processing (or require the caller to explicitly confirm) any topic that wasn't registered for delivery to this exact shop, and avoid exposing `request.shop`/`request.topic` as "verified" fields without additional, out-of-band shop/topic confirmation (e.g., validating the shop domain against an existing session/store record before dispatching to the handler).

### Proof of Concept
Using the same fixtures as `test/webhooks/registry_test.rb`:

```ruby
# Attacker captures a legitimate webhook delivery for their own shop:
body = "{}"
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, body)

legit_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(hmac),
  "x-shopify-shop-domain" => "attacker-shop.myshopify.com",
  "x-shopify-webhook-id" => "attacker-generated-id",
  "x-shopify-api-version" => "2024-01",
}

# Attacker resubmits the exact same body+hmac, forging the shop-domain header:
forged_headers = legit_headers.merge(
  "x-shopify-shop-domain" => "victim-shop.myshopify.com",
)

forged_request = ShopifyAPI::Webhooks::Request.new(raw_body: body, headers: forged_headers)

# Still validates successfully, because hmac only covers `body`, not the shop header:
ShopifyAPI::Utils::HmacValidator.validate(forged_request) # => true

ShopifyAPI::Webhooks::Registry.process(forged_request)
# The registered handler is invoked with data.shop == "victim-shop.myshopify.com",
# even though that shop never sent or authorized this webhook.
``` [7](#0-6)

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
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

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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

**File:** test/webhooks/registry_test.rb (L16-33)
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

        @webhook_request = ShopifyAPI::Webhooks::Request.new(raw_body: "{}", headers: @headers)
        @session = ShopifyAPI::Auth::Session.new(shop: ShopifyAPI::Context.host_name, access_token: "access_token")
        @url = "#{ShopifyAPI::Context.host}/admin/api/#{ShopifyAPI::Context.api_version}/graphql.json"
      end
```
