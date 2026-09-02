Confirmed: `docs/usage/webhooks.md:125-135` explicitly documents that `ShopifyAPI::Webhooks::Registry.process` "will verify the request did indeed come from Shopify," and `data.shop` is documented as "The shop domain of the webhook" (`docs/usage/webhooks.md:14`) — i.e., the gem's own documentation asserts this field is authenticated as part of that verification, when in fact it is not covered by the HMAC.

### Title
Webhook `shop`, `topic`, `webhook_id`, and `api_version` fields are not covered by the HMAC signature, allowing shop-domain spoofing on replay - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook solely via `Utils::HmacValidator.validate(request)`, which computes the HMAC over `Request#to_signable_string`, itself defined as just `@raw_body`. None of `shop`, `topic`, `webhook_id`, or `api_version` — all sourced from unauthenticated HTTP headers — are included in the signed content, yet `data.shop` is handed to the app's handler and documented as trustworthy shop identity.

### Finding Description
`Request#hmac` is derived from the `shopify-hmac-sha256` header and validated against `to_signable_string`, which only returns `@raw_body`:
<cite repo="AYontt/shopify-api-ruby--003" path="lib/shopify_api/webhooks/request.rb" start="35="38" /> [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all pulled straight from headers with zero binding to the signature: [2](#0-1) 

`Registry.process` checks only `Utils::HmacValidator.validate(request)` before dispatching `request.shop`, `request.topic`, etc. into `WebhookMetadata` and the app's handler: [3](#0-2) 

The equality this breaks: the gem implicitly asserts `verified_shop == HMAC-bound(shop)`, but in reality `verified_shop == header(shop)` while `HMAC` binds only `body`. `Utils::HmacValidator.compute_signature` signs `to_signable_string` (the body) with the app's `api_secret_key`: [4](#0-3) 

**Exploit path (unprivileged internet user with only their own shop's install):**
1. An attacker installs the app on their own (attacker-controlled) shop `attacker.myshopify.com` and receives a legitimate webhook delivery — a `(raw_body, shopify-hmac-sha256)` pair that is validly signed with the app's real `api_secret_key`, since Shopify itself computed it for that delivery.
2. The attacker replays that exact `raw_body` and `hmac` header to the app's webhook endpoint, but swaps the `shopify-shop-domain` header to `victim.myshopify.com` (and/or `webhook-id`/`topic`/`api-version` headers as desired).
3. `Utils::HmacValidator.validate` still returns `true`, because it only re-signs `@raw_body`, which is unchanged.
4. `Registry.process` proceeds and calls the handler with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)`, even though the body content and any real signing context belonged to `attacker.myshopify.com`.

Any host application that uses `data.shop` from `ShopifyAPI::Webhooks::WebhookHandler#handle` to select per-tenant state (e.g., which shop's DB row to update, which job queue to enqueue against, or which shop's data to overwrite) — exactly as shown in the gem's own documented example (`perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) — will attribute attacker-supplied webhook content to an arbitrary victim shop identifier, despite `Registry.process`'s HMAC check passing. [5](#0-4) 

### Impact Explanation
This is a cross-tenant data-integrity/confusion issue: an attacker with a legitimate, low-privilege webhook subscription for their own shop can forge the shop-domain association for content delivered under a validly-signed HMAC, causing the host app to process/store data as if it came from a different, victim tenant. This crosses the tenant boundary the gem's own webhook documentation claims to enforce ("verify the request did indeed come from Shopify").

### Likelihood Explanation
Medium: it requires the attacker to first obtain one genuine `(body, hmac)` pair, which is trivially available to any merchant that installs the app (webhooks fire automatically on install/resource changes), and then simply replay it with a modified `shopify-shop-domain`/`topic`/`webhook-id` header to the app's public webhook endpoint.

### Recommendation
Bind `shop`, `topic`, `webhook_id`, and `api_version` into the HMAC-signed content (e.g., include them in `to_signable_string` or otherwise verify that the header-derived shop matches an app-established session/state for that webhook subscription) instead of relying on the caller to trust unauthenticated headers just because the raw body's HMAC is valid. At minimum, document loudly that `data.shop`/`data.topic`/`data.webhook_id` are NOT covered by the HMAC check and must not be trusted for tenant selection without additional verification (e.g., cross-checking against `webhook_id` uniqueness and a previously registered subscription-to-shop mapping).

### Proof of Concept
```ruby
# 1. Attacker's own shop receives a legitimate webhook delivery for topic "orders/create"
raw_body = '{"id": 1, "note": "attacker-controlled content"}'
valid_hmac_b64 = Base64.encode64(
  OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, raw_body)
)

# 2. Attacker replays the exact same body+hmac to the app's webhook endpoint,
#    but forges the shop-domain header to point at a victim shop.
forged_headers = {
  "shopify-topic" => "orders/create",
  "shopify-hmac-sha256" => valid_hmac_b64,     # unchanged, still valid because body is unchanged
  "shopify-shop-domain" => "victim-shop.myshopify.com", # forged
  "shopify-webhook-id" => "attacker-chosen-id",
  "shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)

# 3. HMAC validation passes because it only checks raw_body against the secret.
ShopifyAPI::Webhooks::Registry.process(request)
# => Handler#handle receives data.shop == "victim-shop.myshopify.com" with attacker-controlled body,
#    despite this webhook never having been sent by Shopify for that shop.
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-40)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end

        sig { params(signable_string: String, secret: String).returns(String) }
        def compute_signature(signable_string, secret)
          OpenSSL::HMAC.hexdigest(
            OpenSSL::Digest.new("sha256"),
            secret,
            signable_string,
          )
        end
```

**File:** docs/usage/webhooks.md (L20-29)
```markdown
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
