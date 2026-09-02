I have enough evidence to confirm the vulnerability class. The gem's own documentation states `ShopifyAPI::Webhooks::Registry.process` "will verify the request did indeed come from Shopify," and the `shop` field of `WebhookMetadata` is documented as trustworthy ("The shop domain of the webhook"), but the implementation does not bind the shop identity to the HMAC signature.

### Title
Webhook `shop` field is trusted by the gem's own documentation but excluded from HMAC verification, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies webhook authenticity by validating an HMAC computed only over the raw request body, then hands the caller a `WebhookMetadata` struct whose `shop` field is populated directly from the unauthenticated `X-Shopify-Shop-Domain` header, with no cryptographic binding between the two.

### Finding Description
The equality that should hold is: `shop value used by the app == shop value covered by the verified HMAC signature`. Instead, `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is not part of the signed material: [2](#0-1) 

`Registry.process` validates the HMAC and, on success, unconditionally forwards `request.shop` (the header value) into the handler as the tenant identifier, without any check that it matches a shop for which this HMAC/secret pairing is valid: [3](#0-2) 

`HmacValidator.validate` only compares `verifiable_query.hmac` against a signature computed from `to_signable_string` (the body) — the `shop` field never enters the signable string or the comparison: [4](#0-3) 

Because a single app-level `api_secret_key` signs webhooks for *every* installed shop, any body+HMAC pair that is valid for one merchant (e.g., replayed or intercepted from that merchant's own webhook traffic, or fabricated for a shop the attacker controls, since installing the app on an attacker-owned dev shop yields a genuinely-signed webhook body) remains HMAC-valid when re-sent with a different `X-Shopify-Shop-Domain` header. The gem accepts it as authentic and reports the attacker-chosen shop to the handler.

### Impact Explanation
The library's own documentation instructs developers that `Registry.process` "will verify the request did indeed come from Shopify" and that `data.shop` is "The shop domain of the webhook": [5](#0-4) [6](#0-5) 

Applications built per this documented contract will reasonably use `data.shop` as the trusted tenant key (e.g., to look up the shop's session/access token or to route/store the payload), exactly as shown in the gem's own example (`shop_domain: data.shop`). Since `shop` is not bound to the HMAC, an attacker who can obtain one validly-signed webhook body (trivial: install the app on their own shop, which they fully control, and capture the real webhook Shopify sends them) can resend that same body with a forged `shop-domain` header naming a victim merchant. The gem will report the request as HMAC-valid and attribute it to the victim shop, causing the host application to process attacker-controlled data under another tenant's identity — a cross-tenant confusion/injection primitive.

### Likelihood Explanation
Exploitation only requires: (1) installing the target app on any shop the attacker controls (a normal, unprivileged action for any Shopify Partner/dev account) to obtain one genuinely HMAC-signed webhook body, and (2) POSTing that body to the app's webhook endpoint with a forged shop-domain header. No access token, `client_secret`, or privileged account is needed — the `api_secret_key` is never exposed to or required by the attacker. This is a straightforward, repeatable operation requiring no special access to the victim.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the HMAC-covered signable material, or otherwise cryptographically bind `shop` to the verified body before constructing `WebhookMetadata`, so that a valid HMAC for one shop cannot be replayed to assert a different shop's identity. At minimum, document explicitly that `data.shop` is unauthenticated and must not be trusted as a tenant key without independent verification (e.g., cross-checking against a shop for which the app holds a session).

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`, triggering a real webhook (e.g., `orders/create`) signed with the app's `api_secret_key`. Attacker captures `raw_body` and the `X-Shopify-Hmac-Sha256` header — both valid.
2. Attacker sends a POST to the app's webhook endpoint with the identical `raw_body`/HMAC but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` parses this normally: [7](#0-6) 
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `raw_body` against the HMAC — the forged shop header is irrelevant to the check: [8](#0-7) 
5. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and a validated-looking request, and processes/stores the attacker's body as if it originated from the victim tenant.

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

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```

**File:** docs/usage/webhooks.md (L125-136)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

```ruby
class WebhookController < ApplicationController
  def webhook
    ShopifyAPI::Webhooks::Registry.process(
      ShopifyAPI::Webhooks::Request.new(raw_body: request.raw_post, headers: request.headers.to_h)
    )
    render json: {success: true}.to_json
  end
end
```
```
