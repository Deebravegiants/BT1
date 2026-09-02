### Title
Webhook HMAC signature covers only the raw request body, not the `shop-domain`/`topic`/`webhook-id` headers, allowing cross-tenant webhook spoofing via signature replay - (`lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from unauthenticated HTTP headers. `Utils::HmacValidator.validate` only checks that the *body* was HMAC-signed by Shopify with the app's `api_secret_key` — it never binds the signature to the header values that `Webhooks::Registry.process` subsequently trusts and hands to the app's handler as tenant identity (`shop`). This breaks the identity binding `shop authenticated == shop acted on`.

### Finding Description
`Webhooks::Request#to_signable_string` is defined as: [1](#0-0) 

while `shop`, `topic`, `webhook_id`, and `api_version` are derived purely from headers: [2](#0-1) 

`HmacValidator.validate_signature` computes the HMAC over `verifiable_query.to_signable_string` only (i.e. the raw body), and does not incorporate any header value: [3](#0-2) 

`Webhooks::Registry.process` uses this single HMAC check as the sole authenticity gate before trusting `request.shop`, `request.topic`, and `request.webhook_id`, and forwards them into the app's handler as `WebhookMetadata`: [4](#0-3) 

Because the HMAC only proves "this body was signed with the api_secret_key at some point," and does not prove "this body was signed *for this shop/topic*," an attacker who legitimately controls (or is a customer of) any shop where the target app is installed can capture a genuine, validly-signed webhook delivery (body + `X-Shopify-Hmac-Sha256` header) sent to their own endpoint, then replay that exact body/HMAC pair while substituting the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`, `X-Shopify-Webhook-Id`) header with a victim shop's domain. `HmacValidator.validate` still returns `true` (it only checks the body against the signature), so `Registry.process` will dispatch the handler believing the event originated from the victim shop — an authentication-bypass / cross-tenant confusion analogous to the referenced report's root cause ("a field acted on but not covered by the signature").

### Impact Explanation
This is a **cross-tenant access** vulnerability (Critical per the given rubric): an attacker who has legitimate access to any shop where the app is installed (e.g., their own dev/test store) can forge webhook events that the app's `Webhooks::Registry.process` will process as if they originated from an arbitrary other merchant/shop. Depending on how the app's webhook handlers use `data.shop` (e.g., to select which tenant's records to update, or to trigger `app/uninstalled`-style side effects), this can lead to cross-tenant data corruption, unauthorized state changes for shops the attacker doesn't control, or forced processing of attacker-influenced body content under a victim's shop identity.

### Likelihood Explanation
Moderate-to-high: the attacker only needs to install/operate a single shop with the target app (a normal unprivileged action any internet user can perform for public apps), observe one legitimate webhook delivery from Shopify to their own endpoint, and replay it with a modified `shop-domain` header. No knowledge of `api_secret_key` or any credential belonging to the victim is required — only a header rewrite of an intercepted, self-owned webhook request.

### Recommendation
Include `shop`, `topic`, and `webhook_id` (or at minimum the shop domain) inside `to_signable_string`'s signed content, or independently verify that the `shop-domain` header corresponds to a shop the receiving app instance actually expects/has an active session for, before trusting `request.shop`/`request.topic` in `Webhooks::Registry.process`. At minimum, document prominently that `HmacValidator.validate` only authenticates the body and that callers must independently verify header-derived identity fields.

### Proof of Concept
```ruby
require "shopify_api"
require "openssl"

ShopifyAPI::Context.setup(
  api_key: "key",
  api_secret_key: "shared_app_secret",
  host_name: "app.example.com",
  scope: "read_products",
  is_embedded: false,
)

body = "{}" # generic, shop-agnostic payload, e.g. from a real webhook sent to attacker's own shop
valid_hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), "shared_app_secret", body)

# Attacker captured this exact (body, hmac) pair from a legitimate delivery to
# their own shop "attacker-shop.myshopify.com", then replays it claiming to be
# "victim-shop.myshopify.com":
forged_headers = {
  "x-shopify-topic" => "app/uninstalled",
  "x-shopify-hmac-sha256" => Base64.encode64(valid_hmac),
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # <-- not covered by HMAC
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: body, headers: forged_headers)

ShopifyAPI::Utils::HmacValidator.validate(request) # => true, even though shop header was forged
ShopifyAPI::Webhooks::Registry.process(request)     # handler invoked with shop == "victim-shop.myshopify.com"
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
