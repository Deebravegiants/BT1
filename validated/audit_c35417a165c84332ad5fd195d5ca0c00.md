### Title
Webhook `shop` identity is not covered by the HMAC, allowing a legitimate app-installer to spoof the tenant for otherwise-valid webhook payloads - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body [1](#0-0)  while `shop` is parsed independently from the `shopify-shop-domain`/`x-shopify-shop-domain` header [2](#0-1) . `Utils::HmacValidator.validate` only checks the HMAC against that signable string (the body), never the `shop` header [3](#0-2) . `Registry.process` accepts the request once the body HMAC checks out, then hands `request.shop` straight through to the host application's handler as the tenant identity for that payload [4](#0-3) .

### Finding Description
The intended identity binding is: `shop header == shop whose secret produced this HMAC`. In reality the code only proves `HMAC(body, secret) == received_hmac`; the `shop` header is never part of the signed material. Any entity that can obtain one genuine, validly-signed webhook delivery for *some* shop that has the app installed (i.e., an unprivileged merchant who installs the app on their own store — no special privilege beyond that of any internet user who can install a public app) can capture the `(raw_body, hmac)` pair from their own webhook and replay it to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header value for a victim shop. `HmacValidator.validate` still passes because it never inspects the header, and `Registry.process` forwards `WebhookMetadata.new(... shop: request.shop ...)` — with the attacker-chosen shop — to the app's webhook handler [5](#0-4) . This is exactly the "field acted on but not covered by the HMAC" identity-binding break called out as an analog target: `shop` is consumed by the handler but sits entirely outside the cryptographic proof.

This differs from the OAuth callback and JWT flows in the same gem, where the equivalent identity field (`shop` in `AuthQuery`, `dest` in `JwtPayload`) is explicitly included in the signed/verified payload [6](#0-5) [7](#0-6) , confirming the webhook path is the outlier that fails to bind the tenant identity to the authenticated bytes.

### Impact Explanation
The gem's documented API tells host apps to trust `data.shop` from `WebhookMetadata` as the tenant identifier for routing/persisting webhook data [8](#0-7) . Because that field isn't authenticated, an app relying on it (as the documented usage pattern instructs) can have order/customer/product data attributed to the wrong shop, corrupting or exfiltrating data across tenants — this is a cross-tenant integrity/confidentiality violation reachable by any user who can install the app on a store they control.

### Likelihood Explanation
Requires only the ability to install the target app on any Shopify store (an action any unprivileged internet user/merchant can normally take for public apps) and to replay an HTTP POST with a captured body/HMAC pair while altering one header — no access to `api_secret_key`, tokens, or privileged accounts is needed.

### Recommendation
Include the `shop` (and ideally `topic`/`webhook_id`) header value in the HMAC-signed material, or otherwise cryptographically bind the shop domain to the payload signature, so that `to_signable_string` cannot validate against a body/HMAC pair whose `shop` header has been altered. Alternatively, require and enforce that the shop the webhook claims to be from matches a shop with an active, known installation before invoking the handler.

### Proof of Concept
1. Install the target Shopify app on attacker-controlled store `attacker.myshopify.com`.
2. Register a webhook (e.g., `orders/create`) and capture a delivered request: raw body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(secret, B)`.
3. Replay to the app's webhook endpoint:
   - Headers: `x-shopify-topic: orders/create`, `x-shopify-hmac-sha256: H`, `x-shopify-shop-domain: victim-shop.myshopify.com`
   - Body: `B` (unchanged)
4. `Utils::HmacValidator.validate` succeeds because it only checks `HMAC(B, secret) == H` [3](#0-2) .
5. `Registry.process` invokes the handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", body: B, ...)` [5](#0-4) , causing the host app to attribute attacker-controlled data to the victim tenant.

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

**File:** lib/shopify_api/auth/jwt_payload.rb (L33-41)
```ruby
        @iss = T.let(payload_hash["iss"], String)
        @dest = T.let(payload_hash["dest"], String)
        @aud = T.let(payload_hash["aud"], String)
        @sub = T.let(payload_hash["sub"], T.nilable(String))
        @exp = T.let(payload_hash["exp"], Integer)
        @nbf = T.let(payload_hash["nbf"], Integer)
        @iat = T.let(payload_hash["iat"], Integer)
        @jti = T.let(payload_hash["jti"], String)
        @sid = T.let(payload_hash["sid"], T.nilable(String))
```

**File:** docs/usage/webhooks.md (L10-30)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

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
