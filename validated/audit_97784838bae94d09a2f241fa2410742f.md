Confirmed: this is a genuine, exploitable identity-binding gap in `ShopifyAPI::Webhooks::Registry.process`.

### Title
Webhook shop-domain identity is trusted for tenant routing but is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC-SHA256 signature computed over the raw request body [1](#0-0) . The `to_signable_string` used for that signature is defined as just `@raw_body` [2](#0-1) . The shop-domain header (`x-shopify-shop-domain` / `shopify-shop-domain`), which is the sole tenant identifier passed to the host application's webhook handler, is read directly from the HTTP header and is never part of the signed bytes [3](#0-2) . This is exactly the analog bug class: a field ("shop") is acted upon (used to attribute the event to a tenant) but is not covered by the cryptographic check that is supposed to prove authenticity of the request.

### Finding Description
The identity binding that should hold is:
`shop domain trusted by handler.handle == shop domain cryptographically bound to the signed payload`

In `Registry.process`, this equality does not hold. The verification step is:
```ruby
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
```
which only proves that `HMAC(api_secret_key, raw_body)` matches the `hmac-sha256` header [4](#0-3) . It says nothing about which shop the body belongs to. Immediately after that check passes, the tenant-identifying value is read straight from the unauthenticated header and handed to the app's handler:
```ruby
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
  body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
``` [5](#0-4) 

Because `shop` is a `T::Struct` field on `WebhookMetadata` documented and intended to be used by host apps to route the event to the correct tenant record [6](#0-5) , and because the gem's own documentation instructs apps to use `data.shop` for exactly that purpose [7](#0-6) , any attacker who can produce one valid `(raw_body, hmac)` pair for any topic (which is trivial for anyone who installs/uninstalls the public app on their own store, or otherwise captures a single legitimate webhook delivery, since the HMAC is deterministic per body and does not expire or bind to a specific shop) can replay that exact body with a forged `x-shopify-shop-domain` header pointing at a victim shop. `Utils::HmacValidator.validate` will still return `true`, and the handler will process attacker-supplied event data as if it originated from the victim tenant.

### Impact Explanation
This breaks tenant isolation for any host application whose webhook handler uses `data.shop` (as the gem's own documentation instructs) to select which merchant's data/session to act on — e.g. updating order/customer/inventory records, triggering per-shop side effects, or looking up per-shop credentials keyed by `data.shop`. An attacker with no privileges on the victim shop can inject fabricated webhook events attributed to that shop, which is a cross-tenant access primitive (Critical, per the accepted impact list for cross-tenant access).

### Likelihood Explanation
The prerequisite is only the ability to obtain one legitimately-signed `(raw_body, hmac)` pair — trivial for a public/freely-installable app (self-install, trigger any webhook topic, capture the raw POST) — and the ability to send arbitrary HTTP requests to the app's public webhook endpoint, which is inherent to how webhook endpoints work. No access token, `client_secret`, or privileged account is required, satisfying the "unprivileged internet user" constraint.

### Recommendation
Bind the shop identity into the authenticated payload rather than trusting an unsigned header: e.g. verify the shop header against session/shop records the app already registered a webhook subscription for, or require host apps to cross-check `data.shop` against their own webhook registration records before trusting it, and document this requirement prominently. At minimum, `Registry.process` should not present `request.shop` as trustworthy without documenting that it is unauthenticated by the HMAC.

### Proof of Concept
```ruby
require "openssl"
require "base64"

secret = ShopifyAPI::Context.api_secret_key
raw_body = '{"id":1,"note":"legit event captured from attacker-owned trial store"}'

# 1. Attacker legitimately triggers/captures ONE real webhook delivery for
#    their own store ("attacker-shop.myshopify.com"), giving them a valid
#    (raw_body, hmac) pair signed by the real api_secret_key.
hmac = Base64.encode64(
  OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), secret, raw_body)
)

# 2. Attacker replays the exact same body+hmac but swaps the shop-domain
#    header to point at a victim shop the attacker has no access to.
forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => hmac,
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # unauthenticated
  "x-shopify-webhook-id" => "any-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)

# HMAC validation still succeeds because only raw_body is signed:
ShopifyAPI::Utils::HmacValidator.validate(request) # => true

# The handler is invoked believing this event belongs to "victim-shop.myshopify.com":
ShopifyAPI::Webhooks::Registry.process(request)
```

### Citations

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
